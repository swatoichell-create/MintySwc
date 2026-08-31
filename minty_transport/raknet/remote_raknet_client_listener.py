
from abc import ABC, abstractmethod

class RemoteRakNetClientListener(ABC):
    @abstractmethod
    def on_remote_connected(self, client):
        pass

    @abstractmethod
    def on_remote_payload(self, client, payload: bytes):
        pass

    @abstractmethod
    def on_remote_closed(self, client, reason: str):
        pass
