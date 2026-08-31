import struct
import time
import random
from typing import Optional, Tuple, List
from enum import IntEnum


class RakNetPacketId(IntEnum):
    UNCONNECTED_PING = 0x00
    UNCONNECTED_PING_OPEN_CONNECTIONS = 0x01
    OPEN_CONNECTION_REQUEST_1 = 0x05
    OPEN_CONNECTION_REPLY_1 = 0x06
    OPEN_CONNECTION_REQUEST_2 = 0x07
    OPEN_CONNECTION_REPLY_2 = 0x08
    CONNECTION_REQUEST = 0x09
    CONNECTION_REQUEST_ACCEPTED = 0x10
    NEW_INCOMING_CONNECTION = 0x13
    DISCONNECT_NOTIFICATION = 0x15
    CONNECTED_PING = 0x00
    CONNECTED_PONG = 0x03
    ACK = 0xC0
    NACK = 0xA0
    DATA_PACKET_0 = 0x80
    DATA_PACKET_1 = 0x81
    DATA_PACKET_2 = 0x82
    DATA_PACKET_3 = 0x83
    DATA_PACKET_4 = 0x84
    DATA_PACKET_5 = 0x85
    DATA_PACKET_6 = 0x86
    DATA_PACKET_7 = 0x87
    DATA_PACKET_8 = 0x88
    DATA_PACKET_9 = 0x89
    DATA_PACKET_A = 0x8A
    DATA_PACKET_B = 0x8B
    DATA_PACKET_C = 0x8C
    DATA_PACKET_D = 0x8D
    DATA_PACKET_E = 0x8E
    DATA_PACKET_F = 0x8F


class RakNetReliability(IntEnum):
    UNRELIABLE = 0
    UNRELIABLE_SEQUENCED = 1
    RELIABLE = 2
    RELIABLE_ORDERED = 3
    RELIABLE_SEQUENCED = 4
    UNRELIABLE_WITH_ACK_RECEIPT = 5
    RELIABLE_WITH_ACK_RECEIPT = 6


class RakNetPriority(IntEnum):
    IMMEDIATE = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class RakNetPacket:
    def __init__(self, data: bytes, reliability: RakNetReliability = RakNetReliability.RELIABLE_ORDERED,
                 priority: RakNetPriority = RakNetPriority.MEDIUM, ordering_channel: int = 0):
        self.data = data
        self.reliability = reliability
        self.priority = priority
        self.ordering_channel = ordering_channel
        self.message_index = 0
        self.sequence_index = 0
        self.send_time = time.time()
        self.acknowledged = False
        self.retries = 0
        self.max_retries = 5

    def needs_ack(self) -> bool:
        return self.reliability in [RakNetReliability.RELIABLE, RakNetReliability.RELIABLE_ORDERED,
                                    RakNetReliability.RELIABLE_SEQUENCED, RakNetReliability.RELIABLE_WITH_ACK_RECEIPT]


class RakNetProtocol:
    PROTOCOL_VERSION = 8
    MTU = 1400
    MAX_SPLIT_SIZE = 500
    MAX_PACKET_SIZE = 0x10000
    ACK_DELAY = 0.05
    NACK_DELAY = 0.02
    TIMEOUT = 30.0
    PING_INTERVAL = 5.0

    @staticmethod
    def encode_unconnected_ping(timestamp: int, client_guid: int) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.UNCONNECTED_PING)
        buffer.extend(timestamp.to_bytes(8, byteorder='big', signed=False))
        buffer.extend(RakNetProtocol._encode_magic())
        buffer.extend(client_guid.to_bytes(8, byteorder='big', signed=False))
        return bytes(buffer)

    @staticmethod
    def encode_unconnected_pong(timestamp: int, server_guid: int, advertisement: str) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.UNCONNECTED_PING_OPEN_CONNECTIONS)
        buffer.extend(timestamp.to_bytes(8, byteorder='big', signed=False))
        buffer.extend(RakNetProtocol._encode_magic())
        buffer.extend(server_guid.to_bytes(8, byteorder='big', signed=False))
        buffer.extend(len(advertisement).to_bytes(2, byteorder='big', signed=False))
        buffer.extend(advertisement.encode('utf-8'))
        return bytes(buffer)

    @staticmethod
    def encode_connection_request(client_guid: int, timestamp: int, security: bool = False) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.CONNECTION_REQUEST)
        buffer.extend(client_guid.to_bytes(8, byteorder='big', signed=False))
        buffer.extend(timestamp.to_bytes(8, byteorder='big', signed=False))
        buffer.append(0x00 if not security else 0x01)
        buffer.extend(RakNetProtocol._encode_magic())
        buffer.extend(bytearray(16))
        return bytes(buffer)

    @staticmethod
    def encode_connection_request_accepted(server_address: Tuple[str, int], system_index: int, internal_address: Tuple[str, int], system_addresses: List[Tuple[str, int]], request_timestamp: int, request_timestamp_reply: int) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.CONNECTION_REQUEST_ACCEPTED)
        buffer.extend(RakNetProtocol._encode_address(server_address[0], server_address[1]))
        buffer.extend(system_index.to_bytes(2, byteorder='big', signed=False))
        buffer.extend(RakNetProtocol._encode_address(internal_address[0], internal_address[1]))
        buffer.extend(len(system_addresses).to_bytes(2, byteorder='big', signed=False))
        for addr in system_addresses:
            buffer.extend(RakNetProtocol._encode_address(addr[0], addr[1]))
        buffer.extend(request_timestamp.to_bytes(8, byteorder='big', signed=False))
        buffer.extend(request_timestamp_reply.to_bytes(8, byteorder='big', signed=False))
        return bytes(buffer)

    @staticmethod
    def encode_new_incoming_connection(server_address: Tuple[str, int], internal_address: Tuple[str, int], system_addresses: List[Tuple[str, int]], request_timestamp: int, request_timestamp_reply: int) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.NEW_INCOMING_CONNECTION)
        buffer.extend(RakNetProtocol._encode_address(server_address[0], server_address[1]))
        buffer.extend(RakNetProtocol._encode_address(internal_address[0], internal_address[1]))
        buffer.extend(len(system_addresses).to_bytes(2, byteorder='big', signed=False))
        for addr in system_addresses:
            buffer.extend(RakNetProtocol._encode_address(addr[0], addr[1]))
        buffer.extend(request_timestamp.to_bytes(8, byteorder='big', signed=False))
        buffer.extend(request_timestamp_reply.to_bytes(8, byteorder='big', signed=False))
        return bytes(buffer)

    @staticmethod
    def encode_connected_ping(timestamp: int) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.CONNECTED_PING)
        buffer.extend(timestamp.to_bytes(8, byteorder='big', signed=False))
        return bytes(buffer)

    @staticmethod
    def encode_connected_pong(timestamp: int) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.CONNECTED_PONG)
        buffer.extend(timestamp.to_bytes(8, byteorder='big', signed=False))
        return bytes(buffer)

    @staticmethod
    def encode_disconnect_notification() -> bytes:
        return bytes([RakNetPacketId.DISCONNECT_NOTIFICATION])

    @staticmethod
    def encode_open_connection_request_1(client_guid: int, mtu: int) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.OPEN_CONNECTION_REQUEST_1)
        buffer.extend(RakNetProtocol._encode_magic())
        buffer.append(RakNetProtocol.PROTOCOL_VERSION)
        buffer.extend(mtu.to_bytes(2, byteorder='big', signed=False))
        buffer.extend(client_guid.to_bytes(8, byteorder='big', signed=False))
        return bytes(buffer)

    @staticmethod
    def encode_open_connection_request_2(client_guid: int, server_address: Tuple[str, int], mtu: int) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.OPEN_CONNECTION_REQUEST_2)
        buffer.extend(RakNetProtocol._encode_magic())
        buffer.extend(server_address[1].to_bytes(2, byteorder='big', signed=False))
        buffer.extend(RakNetProtocol._encode_address(server_address[0], server_address[1]))
        buffer.extend(mtu.to_bytes(2, byteorder='big', signed=False))
        buffer.extend(client_guid.to_bytes(8, byteorder='big', signed=False))
        return bytes(buffer)

    @staticmethod
    def encode_connection_request(client_guid: int, timestamp: int, security: bool = False) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.CONNECTION_REQUEST)
        buffer.extend(client_guid.to_bytes(8, byteorder='big', signed=False))
        buffer.extend(timestamp.to_bytes(8, byteorder='big', signed=False))
        buffer.append(1 if security else 0)
        return bytes(buffer)

    @staticmethod
    def encode_frame_set(packets: List[RakNetPacket], sequence_number: int) -> bytes:
        if not packets:
            return b''

        buffer = bytearray()
        packet_id = 0x80 | (sequence_number & 0x0F)
        buffer.append(packet_id)

        for packet in packets:
            frame_header = (packet.reliability << 5) & 0xE0
            frame_header |= 0x10 if packet.message_index > 0 else 0
            frame_header |= 0x08 if packet.sequence_index > 0 else 0
            frame_header |= 0x20 if packet.split_count > 0 else 0

            buffer.append(frame_header)

            if packet.message_index > 0:
                buffer.extend(packet.message_index.to_bytes(3, byteorder='little', signed=False))

            if packet.sequence_index > 0:
                buffer.extend(packet.sequence_index.to_bytes(3, byteorder='little', signed=False))

            if packet.reliability in [2, 3, 4, 6]:
                buffer.append(packet.ordering_channel)

            if packet.split_count > 0:
                buffer.extend(packet.split_count.to_bytes(2, byteorder='big', signed=False))
                buffer.extend(packet.split_id.to_bytes(2, byteorder='big', signed=False))
                buffer.append(packet.split_index)

            buffer.extend(len(packet.data).to_bytes(2, byteorder='big', signed=False))
            buffer.extend(packet.data)

        return bytes(buffer)

    @staticmethod
    def encode_ack(ack_sequence_numbers: List[int]) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.ACK)

        if not ack_sequence_numbers:
            buffer.append(0)
            return bytes(buffer)

        sorted_acks = sorted(ack_sequence_numbers)
        ranges = RakNetProtocol._compress_sequence_numbers(sorted_acks)

        buffer.append(len(ranges))
        for start, end in ranges:
            if start == end:
                buffer.append(0)
                buffer.extend(start.to_bytes(3, byteorder='little', signed=False))
            else:
                buffer.append(1)
                buffer.extend(start.to_bytes(3, byteorder='little', signed=False))
                buffer.extend(end.to_bytes(3, byteorder='little', signed=False))

        return bytes(buffer)

    @staticmethod
    def encode_nack(nack_sequence_numbers: List[int]) -> bytes:
        buffer = bytearray()
        buffer.append(RakNetPacketId.NACK)

        if not nack_sequence_numbers:
            buffer.append(0)
            return bytes(buffer)

        sorted_nacks = sorted(nack_sequence_numbers)
        ranges = RakNetProtocol._compress_sequence_numbers(sorted_nacks)

        buffer.append(len(ranges))
        for start, end in ranges:
            if start == end:
                buffer.append(0)
                buffer.extend(start.to_bytes(3, byteorder='little', signed=False))
            else:
                buffer.append(1)
                buffer.extend(start.to_bytes(3, byteorder='little', signed=False))
                buffer.extend(end.to_bytes(3, byteorder='little', signed=False))

        return bytes(buffer)

    @staticmethod
    def decode_frame_set(data: bytes) -> Tuple[List[Tuple[int, bytes]], int]:
        packets = []
        offset = 0
        sequence_number = 0

        while offset < len(data):
            if offset + 1 > len(data):
                break

            frame_header = data[offset]
            offset += 1

            reliability = (frame_header >> 5) & 0x07
            has_message_index = (frame_header & 0x10) != 0
            has_sequence_index = (frame_header & 0x08) != 0

            if has_message_index and offset + 3 > len(data):
                break
            message_index = int.from_bytes(data[offset:offset+3], byteorder='little') if has_message_index else 0
            offset += 3 if has_message_index else 0

            if has_sequence_index and offset + 3 > len(data):
                break
            sequence_index = int.from_bytes(data[offset:offset+3], byteorder='little') if has_sequence_index else 0
            offset += 3 if has_sequence_index else 0

            ordering_channel = 0
            if reliability in [2, 3, 4, 6]:
                if offset + 1 > len(data):
                    break
                ordering_channel = data[offset]
                offset += 1

            has_split = (frame_header & 0x20) != 0
            split_count = 0
            split_id = 0
            split_index = 0

            if has_split:
                if offset + 4 > len(data):
                    break
                split_count = int.from_bytes(data[offset:offset+2], byteorder='big')
                split_id = int.from_bytes(data[offset+2:offset+4], byteorder='big')
                offset += 4
                if offset + 1 > len(data):
                    break
                split_index = data[offset]
                offset += 1

            length = int.from_bytes(data[offset:offset+2], byteorder='big')
            offset += 2

            if offset + length > len(data):
                break

            packet_data = data[offset:offset+length]
            offset += length

            packets.append((sequence_index, packet_data))

        return packets, sequence_number

    @staticmethod
    def decode_ack(data: bytes) -> List[int]:
        if len(data) < 2 or data[0] != RakNetPacketId.ACK:
            return []

        ack_count = data[1]
        acks = []
        offset = 2

        for _ in range(ack_count):
            if offset + 1 > len(data):
                break

            is_range = data[offset] == 1
            offset += 1

            if offset + 3 > len(data):
                break

            start = int.from_bytes(data[offset:offset+3], byteorder='little')
            offset += 3

            if is_range:
                if offset + 3 > len(data):
                    break
                end = int.from_bytes(data[offset:offset+3], byteorder='little')
                offset += 3
                acks.extend(range(start, end + 1))
            else:
                acks.append(start)

        return acks

    @staticmethod
    def decode_nack(data: bytes) -> List[int]:
        if len(data) < 2 or data[0] != RakNetPacketId.NACK:
            return []

        nack_count = data[1]
        nacks = []
        offset = 2

        for _ in range(nack_count):
            if offset + 1 > len(data):
                break

            is_range = data[offset] == 1
            offset += 1

            if offset + 3 > len(data):
                break

            start = int.from_bytes(data[offset:offset+3], byteorder='little')
            offset += 3

            if is_range:
                if offset + 3 > len(data):
                    break
                end = int.from_bytes(data[offset:offset+3], byteorder='little')
                offset += 3
                nacks.extend(range(start, end + 1))
            else:
                nacks.append(start)

        return nacks

    @staticmethod
    def _encode_magic() -> bytes:
        return bytes([0x00, 0xff, 0xff, 0x00, 0xfe, 0xfe, 0xfe, 0xfe, 0xfd, 0xfd, 0xfd, 0xfd, 0x12, 0x34, 0x56, 0x78])

    @staticmethod
    def _encode_address(host: str, port: int) -> bytes:
        try:
            import socket
            addr_bytes = socket.inet_aton(host)
        except:
            addr_bytes = bytes([127, 0, 0, 1])

        buffer = bytearray()
        buffer.append(4)
        buffer.extend([b ^ 0xff for b in addr_bytes])
        buffer.extend(port.to_bytes(2, byteorder='big', signed=False))
        return bytes(buffer)

    @staticmethod
    def _encode_frame_header(packet: RakNetPacket, sequence_number: int) -> bytes:
        header = 0
        header |= (packet.reliability << 5)

        has_message_index = packet.reliability in [2, 3, 4, 6, 7]
        has_sequence_index = packet.reliability in [1, 3, 4, 7]

        if has_message_index:
            header |= 0x10
        if has_sequence_index:
            header |= 0x08

        buffer = bytearray()
        buffer.append(header)

        if has_message_index:
            buffer.extend(packet.message_index.to_bytes(3, byteorder='little'))
        if has_sequence_index:
            buffer.extend(sequence_number.to_bytes(3, byteorder='little'))

        if packet.reliability in [2, 3, 4, 6]:
            buffer.append(packet.ordering_channel)

        return bytes(buffer)

    @staticmethod
    def _compress_sequence_numbers(numbers: List[int]) -> List[Tuple[int, int]]:
        if not numbers:
            return []

        ranges = []
        start = numbers[0]
        end = numbers[0]

        for num in numbers[1:]:
            if num == end + 1:
                end = num
            else:
                ranges.append((start, end))
                start = num
                end = num

        ranges.append((start, end))
        return ranges
