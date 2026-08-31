import asyncio
import time
import logging
from typing import Dict, List, Set, Optional, Callable
from collections import deque
from .raknet_protocol import RakNetProtocol, RakNetPacket, RakNetReliability, RakNetPriority


class RakNetConnection:
    def __init__(self, guid: int, mtu: int = 1400):
        self.guid = guid
        self.mtu = mtu
        self.logger = logging.getLogger(f"minty_transport.raknet.RakNetConnection.{guid}")

        self.send_sequence_number = 0
        self.receive_sequence_number = 0
        self.message_number = 0

        self.send_queue: Dict[RakNetPriority, deque] = {
            RakNetPriority.IMMEDIATE: deque(),
            RakNetPriority.HIGH: deque(),
            RakNetPriority.MEDIUM: deque(),
            RakNetPriority.LOW: deque()
        }

        self.unacked_packets: Dict[int, RakNetPacket] = {}
        self.ack_queue: Set[int] = set()
        self.nack_queue: Set[int] = set()

        self.received_packets: Dict[int, bytes] = {}
        self.ordered_channels: Dict[int, int] = {}

        self.last_ping_time = 0
        self.last_pong_time = 0
        self.rtt = 0
        self.last_activity = time.time()

        self.connected = False
        self.disconnect_reason = ""

    def send_packet(self, data: bytes, reliability: RakNetReliability = RakNetReliability.RELIABLE_ORDERED,
                    priority: RakNetPriority = RakNetPriority.MEDIUM, ordering_channel: int = 0):
        packet = RakNetPacket(data, reliability, priority, ordering_channel)
        packet.message_index = self.message_number
        self.message_number += 1

        self.send_queue[priority].append(packet)
        self.last_activity = time.time()

    def get_packets_to_send(self, max_size: int) -> List[bytes]:
        packets_to_send = []
        current_size = 0

        for priority in [RakNetPriority.IMMEDIATE, RakNetPriority.HIGH, RakNetPriority.MEDIUM, RakNetPriority.LOW]:
            while self.send_queue[priority] and current_size < max_size:
                packet = self.send_queue[priority].popleft()

                if packet.needs_ack():
                    packet.sequence_index = self.send_sequence_number
                    self.send_sequence_number += 1
                    self.unacked_packets[packet.sequence_index] = packet
                    packet.send_time = time.time()

                encoded = self._encode_packet(packet)
                if current_size + len(encoded) <= max_size:
                    packets_to_send.append(encoded)
                    current_size += len(encoded)
                else:
                    self.send_queue[priority].appendleft(packet)
                    break

        return packets_to_send

    def handle_ack(self, ack_numbers: List[int]):
        for ack_num in ack_numbers:
            if ack_num in self.unacked_packets:
                packet = self.unacked_packets.pop(ack_num)
                packet.acknowledged = True
                self.logger.debug(f"Packet {ack_num} acknowledged")

    def handle_nack(self, nack_numbers: List[int]) -> List[RakNetPacket]:
        retransmit = []
        for nack_num in nack_numbers:
            if nack_num in self.unacked_packets:
                packet = self.unacked_packets[nack_num]
                packet.retries += 1
                if packet.retries < packet.max_retries:
                    retransmit.append(packet)
                    self.logger.debug(f"Retransmitting packet {nack_num}, attempt {packet.retries}")
                else:
                    self.unacked_packets.pop(nack_num)
                    self.logger.warning(f"Packet {nack_num} exceeded max retries")
        return retransmit

    def handle_frame_set(self, frame_data: bytes) -> List[bytes]:
        packets, sequence_number = RakNetProtocol.decode_frame_set(frame_data)
        received = []

        for seq_num, packet_data in packets:
            if seq_num not in self.received_packets:
                self.received_packets[seq_num] = packet_data
                self.ack_queue.add(seq_num)
                self.last_activity = time.time()

                ordering_channel = self._extract_ordering_channel(packet_data)
                if ordering_channel is not None:
                    received.append(packet_data)

        return received

    def get_ack_packet(self) -> Optional[bytes]:
        if not self.ack_queue:
            return None

        ack_numbers = list(self.ack_queue)
        self.ack_queue.clear()
        return RakNetProtocol.encode_ack(ack_numbers)

    def get_nack_packet(self) -> Optional[bytes]:
        if not self.nack_queue:
            return None

        expected = self.receive_sequence_number
        missing = []

        for i in range(expected, max(self.received_packets.keys()) + 1):
            if i not in self.received_packets:
                missing.append(i)

        if missing:
            self.nack_queue.clear()
            return RakNetProtocol.encode_nack(missing)

        return None

    def check_timeouts(self, current_time: float) -> List[RakNetPacket]:
        retransmit = []
        timeout_threshold = current_time - (self.rtt * 2 if self.rtt > 0 else 1.0)

        for seq_num, packet in list(self.unacked_packets.items()):
            if packet.send_time < timeout_threshold:
                packet.retries += 1
                if packet.retries < packet.max_retries:
                    retransmit.append(packet)
                    packet.send_time = current_time
                    self.logger.debug(f"Timeout retransmit for packet {seq_num}")
                else:
                    self.unacked_packets.pop(seq_num)
                    self.logger.warning(f"Packet {seq_num} timeout exceeded")

        return retransmit

    def update_rtt(self, rtt: float):
        if self.rtt == 0:
            self.rtt = rtt
        else:
            self.rtt = (self.rtt * 0.9) + (rtt * 0.1)

    def check_connection_timeout(self, current_time: float) -> bool:
        if current_time - self.last_activity > RakNetProtocol.TIMEOUT:
            self.disconnect_reason = "timeout"
            return True
        return False

    def _encode_packet(self, packet: RakNetPacket) -> bytes:
        return RakNetProtocol.encode_frame_set([packet], packet.sequence_index)

    def encode_packet(self, packet: RakNetPacket) -> bytes:
        return self._encode_packet(packet)

    def _extract_ordering_channel(self, packet_data: bytes) -> Optional[int]:
        if len(packet_data) < 1:
            return None
        return packet_data[0] & 0x07

    def cleanup_old_packets(self, current_time: float):
        old_threshold = current_time - RakNetProtocol.TIMEOUT
        self.received_packets = {k: v for k, v in self.received_packets.items()
                                if k >= self.receive_sequence_number}

        if self.received_packets:
            min_received = min(self.received_packets.keys())
            if min_received > self.receive_sequence_number:
                self.receive_sequence_number = min_received
