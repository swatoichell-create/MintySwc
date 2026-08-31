import asyncio
import logging
import random
from typing import Dict, Tuple
from .raknet_protocol import RakNetProtocol, RakNetPacketId
from .raknet_connection import RakNetConnection
from .local_raknet_server_listener import LocalRakNetServerListener
from .local_raknet_session import LocalRakNetSession

class LocalRakNetServer:
    def __init__(self, bind_address: Tuple[str, int], advertisement: str, listener: LocalRakNetServerListener):
        self.bind_address = bind_address
        self.advertisement = advertisement
        self.listener = listener
        self.logger = logging.getLogger("minty_transport.raknet.LocalRakNetServer")
        self.sessions: Dict[Tuple[str, int], LocalRakNetSession] = {}
        self.server_guid = random.getrandbits(64)
        self._transport = None
        self._protocol = None
        self._running = False

    async def start(self):
        loop = asyncio.get_event_loop()
        self._transport, self._protocol = await loop.create_datagram_endpoint(
            lambda: _RakNetServerProtocol(self),
            local_addr=self.bind_address
        )
        self._running = True
        self.logger.info(f"Listening for 0.15.10 clients on {self.bind_address}")

    def stop(self):
        for session in list(self.sessions.values()):
            session.close_from_proxy("server shutdown")
        if self._transport:
            self._transport.close()
        self._running = False

    def remove_session(self, session: LocalRakNetSession):
        if session.client_address in self.sessions:
            del self.sessions[session.client_address]

class _RakNetServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, server: LocalRakNetServer):
        self.server = server
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        try:
            packet_id = data[0] if data else 0

            if packet_id == RakNetPacketId.UNCONNECTED_PING:
                self._handle_unconnected_ping(data, addr)
            elif packet_id == RakNetPacketId.OPEN_CONNECTION_REQUEST_1:
                self._handle_open_connection_request_1(data, addr)
            elif packet_id == RakNetPacketId.OPEN_CONNECTION_REQUEST_2:
                self._handle_open_connection_request_2(data, addr)
            elif addr in self.server.sessions:
                session = self.server.sessions[addr]
                session.receive(data)
        except Exception as e:
            self.server.logger.error(f"Error processing datagram from {addr}: {e}")

    def _handle_unconnected_ping(self, data, addr):
        try:
            if len(data) < 25:
                return

            timestamp = int.from_bytes(data[1:9], byteorder='big')
            magic = data[9:25]

            if magic != RakNetProtocol._encode_magic():
                return

            response = RakNetProtocol.encode_unconnected_ping(timestamp, self.server.server_guid)
            self.transport.sendto(response, addr)
        except Exception as e:
            self.server.logger.error(f"Error handling unconnected ping: {e}")

    def _handle_open_connection_request_1(self, data, addr):
        try:
            if len(data) < 28:
                return

            magic = data[1:17]
            protocol_version = data[17]
            mtu = int.from_bytes(data[18:20], byteorder='big')
            client_guid = int.from_bytes(data[20:28], byteorder='big')

            if magic != RakNetProtocol._encode_magic():
                return

            if protocol_version != RakNetProtocol.PROTOCOL_VERSION:
                return

            response = bytearray()
            response.append(RakNetPacketId.OPEN_CONNECTION_REPLY_1)
            response.extend(RakNetProtocol._encode_magic())
            response.extend(self.server.server_guid.to_bytes(8, byteorder='big'))
            response.append(0)
            response.extend(mtu.to_bytes(2, byteorder='big'))

            self.transport.sendto(bytes(response), addr)
        except Exception as e:
            self.server.logger.error(f"Error handling open connection request 1: {e}")

    def _handle_open_connection_request_2(self, data, addr):
        try:
            if len(data) < 33:
                return

            magic = data[1:17]
            server_address = self._decode_address(data[17:25])
            mtu = int.from_bytes(data[25:27], byteorder='big')
            client_guid = int.from_bytes(data[27:35], byteorder='big')

            if magic != RakNetProtocol._encode_magic():
                return

            session = LocalRakNetSession(self.server, addr, self.server.listener, client_guid)
            self.server.sessions[addr] = session
            session.open()

            response = bytearray()
            response.append(RakNetPacketId.OPEN_CONNECTION_REPLY_2)
            response.extend(RakNetProtocol._encode_magic())
            response.extend(self.server.server_guid.to_bytes(8, byteorder='big'))
            response.extend(addr[1].to_bytes(2, byteorder='big'))
            response.extend(RakNetProtocol._encode_address(addr[0], addr[1]))
            response.extend(mtu.to_bytes(2, byteorder='big'))
            response.append(0)

            self.transport.sendto(bytes(response), addr)
        except Exception as e:
            self.server.logger.error(f"Error handling open connection request 2: {e}")

    def _decode_address(self, data):
        if len(data) < 7:
            return ("127.0.0.1", 19132)

        version = data[0]
        if version != 4:
            return ("127.0.0.1", 19132)

        ip_bytes = [b ^ 0xff for b in data[1:5]]
        host = ".".join(str(b) for b in ip_bytes)
        port = int.from_bytes(data[5:7], byteorder='big')
        return (host, port)

    def connection_lost(self, exc):
        if exc:
            self.server.logger.error(f"Server connection lost: {exc}")
