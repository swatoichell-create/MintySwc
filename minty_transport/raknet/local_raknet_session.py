import logging
import time
from typing import Tuple
from .raknet_connection import RakNetConnection
from .raknet_protocol import RakNetProtocol, RakNetReliability, RakNetPriority
from .local_raknet_server_listener import LocalRakNetServerListener

class LocalRakNetSession:
    def __init__(self, server, client_address: Tuple[str, int], listener: LocalRakNetServerListener, client_guid: int):
        self.server = server
        self.client_address = client_address
        self.listener = listener
        self.client_guid = client_guid
        self.logger = logging.getLogger("minty_transport.raknet.LocalRakNetSession")
        self._connection = RakNetConnection(client_guid)
        self._closed = False
        self._transport = None

    @property
    def closed(self) -> bool:
        return self._closed

    def set_transport(self, transport):
        self._transport = transport

    def send_game(self, payload: bytes):
        if not self._closed and self._transport:
            self._connection.send_packet(payload, RakNetReliability.RELIABLE_ORDERED, RakNetPriority.MEDIUM, 0)
            packets = self._connection.get_packets_to_send(self._connection.mtu)
            for packet in packets:
                self._transport.sendto(packet, self.client_address)

    def close_from_proxy(self, reason: str):
        self._close_internal(reason, notify_listener=False)

    def open(self):
        if self._closed:
            return
        self.logger.info(f"Client RakNet session opened: {self.client_address}")
        self.listener.on_client_connected(self)

    def receive(self, payload: bytes):
        if not payload or self._closed:
            return

        packet_id = payload[0] if payload else 0

        if 0x80 <= packet_id <= 0x8F:
            self._handle_frame_set(payload[1:])
        elif packet_id == 0xC0:
            ack_numbers = RakNetProtocol.decode_ack(payload)
            self._connection.handle_ack(ack_numbers)
        elif packet_id == 0xA0:
            nack_numbers = RakNetProtocol.decode_nack(payload)
            retransmit = self._connection.handle_nack(nack_numbers)
            for packet in retransmit:
                encoded = self._connection._encode_packet(packet)
                self._transport.sendto(encoded, self.client_address)
        elif packet_id == RakNetPacketId.CONNECTED_PING:
            self._handle_connected_ping(payload)
        elif packet_id == RakNetPacketId.CONNECTED_PONG:
            self._handle_connected_pong(payload)
        elif packet_id == RakNetPacketId.DISCONNECT_NOTIFICATION:
            self.close_from_proxy("client disconnect")
        else:
            self.listener.on_client_payload(self, payload)

    def _handle_frame_set(self, frame_data: bytes):
        packets = self._connection.handle_frame_set(frame_data)
        for packet_data in packets:
            self.listener.on_client_payload(self, packet_data)

        ack_packet = self._connection.get_ack_packet()
        if ack_packet and self._transport:
            ack_data = bytes([0xC0]) + ack_packet
            self._transport.sendto(ack_data, self.client_address)

    def _handle_connected_ping(self, data: bytes):
        if len(data) >= 9 and self._transport:
            timestamp = int.from_bytes(data[1:9], byteorder='big')
            pong = RakNetProtocol.encode_connected_pong(timestamp)
            self._transport.sendto(pong, self.client_address)

    def _handle_connected_pong(self, data: bytes):
        pass

    def _close_internal(self, reason: str, notify_listener: bool):
        if self._closed:
            return
        self._closed = True
        self.logger.info(f"local {self.client_address[0]}:{self.client_address[1]} closed: {reason}")
        self.server.remove_session(self)
        if notify_listener:
            self.listener.on_client_closed(self, reason)
