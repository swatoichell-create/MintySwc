
import asyncio
import logging
from typing import Dict, Tuple
from ..raknet.local_raknet_server import LocalRakNetServer
from ..raknet.local_raknet_server_listener import LocalRakNetServerListener
from ..raknet.local_raknet_session import LocalRakNetSession
from .proxy_bridge import ProxyBridge

class MintyProxy(LocalRakNetServerListener):
    def __init__(self, local_address: Tuple[str, int], target_address: Tuple[str, int]):
        self.local_address = local_address
        self.target_address = target_address
        self.logger = logging.getLogger("minty_transport.proxy.MintyProxy")
        self.bridges: Dict[LocalRakNetSession, ProxyBridge] = {}
        self.server = LocalRakNetServer(
            bind_address=local_address,
            advertisement="MCPE;MintySwc;MintySwc Proxy;84;0.15.10;0;10;123456789;Survival;Survival;1;19132;19133",
            listener=self,
        )
        self._running = False

    async def start(self):
        await self.server.start()
        self.logger.info(f"Proxying 0.15.10 clients to 0.14.3 server {self.target_address}")
        self._running = True

    async def stop(self):
        for bridge in list(self.bridges.values()):
            await bridge.close("proxy shutdown")
        self.server.stop()
        self._running = False

    def on_client_connected(self, session: LocalRakNetSession):
        bridge = ProxyBridge(
            local_session=session,
            target_address=self.target_address,
            on_closed=lambda closed_session: self._remove_bridge(closed_session),
        )
        self.bridges[session] = bridge
        asyncio.create_task(bridge.start())

    def on_client_payload(self, session: LocalRakNetSession, payload: bytes):
        bridge = self.bridges.get(session)
        if bridge:
            asyncio.create_task(bridge.from_client(payload))

    def on_client_closed(self, session: LocalRakNetSession, reason: str):
        bridge = self.bridges.pop(session, None)
        if bridge:
            asyncio.create_task(bridge.close(reason))

    def _remove_bridge(self, session: LocalRakNetSession):
        if session in self.bridges:
            del self.bridges[session]
