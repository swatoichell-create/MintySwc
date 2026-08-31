import asyncio
import logging
import random
import time
from typing import Tuple
from .raknet_protocol import RakNetProtocol, RakNetReliability, RakNetPriority, RakNetPacketId
from .raknet_connection import RakNetConnection
from .remote_raknet_client_listener import RemoteRakNetClientListener

class RemoteRakNetClient:
    def __init__(self, target_address: Tuple[str, int], listener: RemoteRakNetClientListener):
        self.target_address = target_address
        self.listener = listener
        self.logger = logging.getLogger("minty_transport.raknet.RemoteRakNetClient")
        self.client_guid = random.getrandbits(64)
        self._connection = RakNetConnection(self.client_guid)
        self._transport = None
        self._connected = False
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def connected(self) -> bool:
        return self._connected and not self._closed

    async def start(self):
        loop = asyncio.get_event_loop()
        self._transport, _ = await loop.create_datagram_endpoint(
            lambda: _RakNetClientProtocol(self),
            remote_addr=self.target_address
        )
        self.logger.info(f"Connecting RakNet client to {self.target_address}")

        await self._send_unconnected_ping()
        await asyncio.sleep(0.1)
        await self._send_open_connection_request_1()
        await asyncio.sleep(0.1)
        await self._send_open_connection_request_2()

        asyncio.create_task(self._connection_maintenance())

    def send_game(self, payload: bytes):
        if not self._closed and self._connected:
            self._connection.send_packet(payload, RakNetReliability.RELIABLE_ORDERED, RakNetPriority.MEDIUM, 0)
            packets = self._connection.get_packets_to_send(self._connection.mtu)
            for packet in packets:
                self._transport.sendto(packet)

    async def close(self, reason: str):
        self._close_internal(reason, notify_listener=True)

    def open(self):
        if self._closed:
            return
        self._connected = True
        self.logger.info(f"Remote RakNet session opened: {self.target_address}")
        self.listener.on_remote_connected(self)

    def receive(self, payload: bytes):
        if not payload or self._closed:
            return

        packet_id = payload[0] if payload else 0

        if packet_id == 0x80:
            self._handle_frame_set(payload[1:])
        elif packet_id == 0xC0:
            ack_numbers = RakNetProtocol.decode_ack(payload)
            self._connection.handle_ack(ack_numbers)
        elif packet_id == 0xA0:
            nack_numbers = RakNetProtocol.decode_nack(payload)
            retransmit = self._connection.handle_nack(nack_numbers)
            for packet in retransmit:
                encoded = self._connection._encode_packet(packet)
                self._transport.sendto(encoded)
        else:
            self.listener.on_remote_payload(self, payload)

    def close_from_channel(self, reason: str):
        self._close_internal(reason, notify_listener=True)

    def fail(self, cause: Exception):
        self.logger.warning(f"Remote RakNet channel error for {self.target_address}: {cause}")
        self._close_internal("session error", notify_listener=True)

    async def _send_unconnected_ping(self):
        timestamp = int(time.time() * 1000)
        packet = RakNetProtocol.encode_unconnected_ping(timestamp, self.client_guid)
        self._transport.sendto(packet)

    async def _send_open_connection_request_1(self):
        packet = RakNetProtocol.encode_open_connection_request_1(self.client_guid, self._connection.mtu)
        self._transport.sendto(packet)

    async def _send_open_connection_request_2(self):
        packet = RakNetProtocol.encode_open_connection_request_2(self.client_guid, self.target_address, self._connection.mtu)
        self._transport.sendto(packet)

    async def _connection_maintenance(self):
        while not self._closed:
            await asyncio.sleep(0.1)
            current_time = time.time()

            retransmit = self._connection.check_timeouts(current_time)
            for packet in retransmit:
                encoded = self._connection._encode_packet(packet)
                self._transport.sendto(encoded)

            ack_packet = self._connection.get_ack_packet()
            if ack_packet:
                ack_data = bytes([0xC0]) + ack_packet
                self._transport.sendto(ack_data)

            nack_packet = self._connection.get_nack_packet()
            if nack_packet:
                nack_data = bytes([0xA0]) + nack_packet
                self._transport.sendto(nack_data)

            if self._connection.check_connection_timeout(current_time):
                self.close_from_channel("timeout")

            self._connection.cleanup_old_packets(current_time)

    def _handle_frame_set(self, frame_data: bytes):
        packets = self._connection.handle_frame_set(frame_data)
        for packet_data in packets:
            self.listener.on_remote_payload(self, packet_data)

        ack_packet = self._connection.get_ack_packet()
        if ack_packet:
            ack_data = bytes([0xC0]) + ack_packet
            self._transport.sendto(ack_data)

    def _close_internal(self, reason: str, notify_listener: bool):
        if self._closed:
            return
        self._closed = True
        self._connected = False
        self.logger.info(f"remote {self.target_address[0]}:{self.target_address[1]} closed: {reason}")
        if self._transport:
            self._transport.close()
        if notify_listener:
            self.listener.on_remote_closed(self, reason)

class _RakNetClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, client: RemoteRakNetClient):
        self.client = client
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.client._transport = transport

    def datagram_received(self, data, addr):
        packet_id = data[0] if data else 0

        if packet_id == RakNetPacketId.OPEN_CONNECTION_REPLY_1:
            self.client.open()
        elif packet_id == RakNetPacketId.OPEN_CONNECTION_REPLY_2:
            pass
        else:
            self.client.receive(data)

    def connection_lost(self, exc):
        if exc:
            self.client.logger.error(f"Client connection lost: {exc}")
        self.client.close_from_channel("connection lost")
