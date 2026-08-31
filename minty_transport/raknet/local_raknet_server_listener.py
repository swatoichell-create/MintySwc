
from abc import ABC, abstractmethod

class LocalRakNetServerListener(ABC):
    @abstractmethod
    def on_client_connected(self, session):
        pass

    @abstractmethod
    def on_client_payload(self, session, payload: bytes):
        pass

    @abstractmethod
    def on_client_closed(self, session, reason: str):
        pass
