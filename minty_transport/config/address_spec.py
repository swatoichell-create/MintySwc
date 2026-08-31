
import socket
from typing import Tuple

class AddressSpec:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def to_bind_address(self) -> Tuple[str, int]:
        return (self.host, self.port)

    def to_remote_address(self) -> Tuple[str, int]:
        remote_host = "127.0.0.1" if self.host in ("0.0.0.0", "::") else self.host
        return (remote_host, self.port)

    @staticmethod
    def parse(value: str) -> 'AddressSpec':
        trimmed = value.strip()
        separator = trimmed.rfind(":")
        if separator <= 0 or separator >= len(trimmed) - 1:
            raise ValueError(f"Address must be in host:port form: {value}")

        host = trimmed[:separator]
        port_str = trimmed[separator + 1:]
        try:
            port = int(port_str)
        except ValueError:
            raise ValueError(f"Address port is not a number: {value}")

        if not (1 <= port <= 65535):
            raise ValueError(f"Address port is out of range: {value}")

        return AddressSpec(host, port)
