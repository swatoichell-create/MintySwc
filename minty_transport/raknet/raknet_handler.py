import logging
from .raknet_endpoint import RakNetEndpoint

class RakNetHandler:
    def __init__(self, endpoint: RakNetEndpoint):
        self.endpoint = endpoint
        self.logger = logging.getLogger("minty_transport.raknet.RakNetHandler")

    def on_channel_active(self):
        self.endpoint.open()

    def on_data_received(self, data: bytes):
        self.endpoint.receive(data)

    def on_channel_inactive(self):
        self.endpoint.close_from_channel(self.endpoint.channel_inactive_reason)

    def on_error(self, error: Exception):
        self.endpoint.fail(error)
