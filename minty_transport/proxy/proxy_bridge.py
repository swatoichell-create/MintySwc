import asyncio
import logging
from typing import Callable, Deque, Dict
from collections import deque
from threading import Lock
from ..raknet.local_raknet_session import LocalRakNetSession
from ..raknet.remote_raknet_client import RemoteRakNetClient
from ..raknet.remote_raknet_client_listener import RemoteRakNetClientListener
from ..mcpe.mcpe_translator import McpeTranslator
from ..mcpe.mcpe_packet_inspector import McpePacketInspector

class ProxyBridge(RemoteRakNetClientListener):
    def __init__(
        self,
        local_session: LocalRakNetSession,
        target_address: tuple,
        on_closed: Callable[[LocalRakNetSession], None],
    ):
        self.local_session = local_session
        self.target_address = target_address
        self.on_closed = on_closed
        self.logger = logging.getLogger("minty_transport.proxy.ProxyBridge")

        self._lock = Lock()
        self._pending_client_payloads: Deque[bytes] = deque()
        self._remote_client = RemoteRakNetClient(target_address, self)
        self._inspector = McpePacketInspector()
        self._dropped_unsupported: Dict[int, int] = {}
        self._closed = False
        self._remote_ready_for_game = False
        self._client_payloads = 0
        self._remote_payloads = 0
        self._local_payloads = 0

    async def start(self):
        try:
            await self._remote_client.start()
        except Exception as e:
            self.logger.error(f"Failed to start remote client: {e}", exc_info=True)
            await self.close("start failed")

    async def from_client(self, payload: bytes):
        try:
            translated = McpeTranslator.client_to_server(payload, self._inspector, record_drop=self._record_drop)
            if not translated:
                return

            with self._lock:
                if self._closed:
                    return
                self._client_payloads += 1
                if not self._remote_ready_for_game:
                    for pkt in translated:
                        self._pending_client_payloads.append(pkt)
                    send_now = None
                else:
                    send_now = translated

            if send_now:
                for pkt in send_now:
                    self.logger.debug(f"Sending translated client payload to remote: {self._payload_summary(pkt)}")
                    self._remote_client.send_game(pkt)
        except Exception as e:
            self.logger.error(f"Error in from_client: {e}", exc_info=True)

    async def close(self, reason: str):
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._log_closing("Proxy bridge closing", reason)
            self._pending_client_payloads.clear()

        if not self._remote_client.closed:
            await self._remote_client.close(reason)
        self.on_closed(self.local_session)

    def on_remote_connected(self, client: RemoteRakNetClient):
        self.logger.info(f"Proxy bridge RakNet ready for {self.target_address}, delaying MCPE login flush")

        async def flush_delayed():
            await asyncio.sleep(0.15)
            with self._lock:
                if self._closed:
                    return
                self._remote_ready_for_game = True
                self.logger.info(
                    f"Proxy bridge ready for {self.target_address}, flushing {len(self._pending_client_payloads)} queued MCPE packet(s)"
                )
                queued = list(self._pending_client_payloads)
                self._pending_client_payloads.clear()

            for payload in queued:
                self.logger.debug(f"Flushing translated client payload to remote: {self._payload_summary(payload)}")
                client.send_game(payload)

        asyncio.create_task(flush_delayed())

    def on_remote_payload(self, client: RemoteRakNetClient, payload: bytes):
        with self._lock:
            if self._closed:
                return
            self._remote_payloads += 1
            first_remote_payload = self._remote_payloads == 1

        if first_remote_payload:
            self.logger.debug(f"First MCPE payload received from {self.target_address}")

        for translated in McpeTranslator.server_to_client(payload, record_drop=self._record_drop):
            with self._lock:
                if self._closed:
                    return
                self._local_payloads += 1
                first_local_payload = self._local_payloads == 1

            if first_local_payload:
                self.logger.debug(f"First translated MCPE payload sent to local client from {self.target_address}")

            self.local_session.send_game(translated)

    def on_remote_closed(self, client: RemoteRakNetClient, reason: str):
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._log_closing("Proxy bridge remote closed", reason)
            self._pending_client_payloads.clear()

        self.local_session.close_from_proxy(f"remote {reason}")
        self.on_closed(self.local_session)

    def _record_drop(self, packet_id: int):
        with self._lock:
            self._dropped_unsupported[packet_id] = self._dropped_unsupported.get(packet_id, 0) + 1

    def _log_closing(self, prefix: str, reason: str):
        self.logger.info(
            f"{prefix} for {self.target_address}: reason={reason}, "
            f"clientPayloads={self._client_payloads}, remotePayloads={self._remote_payloads}, "
            f"localPayloads={self._local_payloads}, queued={len(self._pending_client_payloads)}, "
            f"droppedUnsupported={self._format_drops()}"
        )

    def _format_drops(self) -> str:
        return "{" + ", ".join(f"0x{packet_id:x}={count}" for packet_id, count in self._dropped_unsupported.items()) + "}"

    def _payload_summary(self, payload: bytes) -> str:
        prefix = " ".join(f"{b:02x}" for b in payload[:8])
        return f"len={len(payload)} prefix={prefix}"
