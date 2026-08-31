
import struct
import socket
from typing import Tuple
from uuid import UUID

class ByteReader:
    def __init__(self, data: bytes, offset: int = 0):
        self.data = data
        self.offset = offset

    @property
    def remaining(self) -> int:
        return len(self.data) - self.offset

    def has_remaining(self) -> bool:
        return self.offset < len(self.data)

    def skip(self, length: int):
        if length < 0 or self.offset + length > len(self.data):
            raise ValueError(f"Cannot skip {length} bytes")
        self.offset += length

    def byte(self) -> int:
        if self.offset >= len(self.data):
            raise ValueError("Unexpected end of buffer")
        value = self.data[self.offset]
        self.offset += 1
        return value

    def u_byte(self) -> int:
        return self.byte() & 0xff

    def bytes(self, length: int) -> bytes:
        if length < 0 or self.offset + length > len(self.data):
            raise ValueError(f"Cannot read {length} bytes")
        out = self.data[self.offset:self.offset + length]
        self.offset += length
        return out

    def int_be(self) -> int:
        value = 0
        for _ in range(4):
            value = (value << 8) | self.u_byte()
        return value

    def int_le(self) -> int:
        value = 0
        for shift in range(0, 25, 8):
            value |= self.u_byte() << shift
        return value

    def float_be(self) -> float:
        return struct.unpack(">f", self.bytes(4))[0]

    def float_le(self) -> float:
        return struct.unpack("<f", self.bytes(4))[0]

    def short_be(self) -> int:
        return (self.u_byte() << 8) | self.u_byte()

    def short_le(self) -> int:
        return self.u_byte() | (self.u_byte() << 8)

    def l_triad(self) -> int:
        return self.u_byte() | (self.u_byte() << 8) | (self.u_byte() << 16)

    def long_be(self) -> int:
        value = 0
        for _ in range(8):
            value = (value << 8) | self.u_byte()
        return value

    def uuid(self) -> UUID:
        high = self.long_be()
        low = self.long_be()
        return UUID(int=(high << 64) | low)

    def string_be(self) -> str:
        length = self.short_be()
        return self.bytes(length).decode("utf-8")

    def address(self) -> Tuple[str, int]:
        version = self.u_byte()
        if version != 4:
            raise ValueError(f"Only RakNet IPv4 addresses are supported, got version {version}")
        parts = [self.u_byte() ^ 0xff for _ in range(4)]
        host = ".".join(str(p) for p in parts)
        port = self.short_be()
        return (host, port)
