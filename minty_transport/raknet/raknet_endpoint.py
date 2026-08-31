
from abc import ABC, abstractmethod

class RakNetEndpoint(ABC):
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def receive(self, payload: bytes):
        pass

    @abstractmethod
    def close_from_channel(self, reason: str):
        pass

    @abstractmethod
    def fail(self, cause: Exception):
        pass

    @property
    @abstractmethod
    def channel_inactive_reason(self) -> str:
        pass
