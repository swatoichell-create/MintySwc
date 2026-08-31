
import struct
import socket
from typing import Tuple
from uuid import UUID

class ByteWriter:
    def __init__(self):
        self._buffer = bytearray()

    @property
    def size(self) -> int:
        return len(self._buffer)

    def byte(self, value: int) -> 'ByteWriter':
        self._buffer.append(value & 0xff)
        return self

    def bytes(self, value: bytes) -> 'ByteWriter':
        self._buffer.extend(value)
        return self

    def bytes_slice(self, value: bytes, offset: int, length: int) -> 'ByteWriter':
        if offset < 0 or length < 0 or offset + length > len(value):
            raise ValueError(f"Cannot write {length} bytes")
        self._buffer.extend(value[offset:offset + length])
        return self

    def int_be(self, value: int) -> 'ByteWriter':
        for shift in range(24, -1, -8):
            self.byte((value >> shift) & 0xff)
        return self

    def int_le(self, value: int) -> 'ByteWriter':
        for shift in range(0, 25, 8):
            self.byte((value >> shift) & 0xff)
        return self

    def float_be(self, value: float) -> 'ByteWriter':
        return self.int_be(struct.unpack(">I", struct.pack(">f", value))[0])

    def float_le(self, value: float) -> 'ByteWriter':
        return self.int_le(struct.unpack("<I", struct.pack("<f", value))[0])

    def short_be(self, value: int) -> 'ByteWriter':
        self.byte((value >> 8) & 0xff)
        self.byte(value & 0xff)
        return self

    def short_le(self, value: int) -> 'ByteWriter':
        self.byte(value & 0xff)
        self.byte((value >> 8) & 0xff)
        return self

    def l_triad(self, value: int) -> 'ByteWriter':
        self.byte(value & 0xff)
        self.byte((value >> 8) & 0xff)
        self.byte((value >> 16) & 0xff)
        return self

    def long_be(self, value: int) -> 'ByteWriter':
        for shift in range(56, -1, -8):
            self.byte((value >> shift) & 0xff)
        return self

    def uuid(self, value: UUID) -> 'ByteWriter':
        int_value = value.int
        self.long_be((int_value >> 64) & 0xffffffffffffffff)
        self.long_be(int_value & 0xffffffffffffffff)
        return self

    def string_be(self, value: str) -> 'ByteWriter':
        encoded = value.encode("utf-8")
        if len(encoded) > 0xffff:
            raise ValueError("String is too long for RakNet/MCPE short string")
        self.short_be(len(encoded))
        self.bytes(encoded)
        return self

    def address(self, host: str, port: int) -> 'ByteWriter':
        raw = socket.inet_aton(host)
        if len(raw) != 4:
            raise ValueError(f"Only IPv4 addresses are supported for RakNet packets: {host}")
        self.byte(4)
        for byte in raw:
            self.byte(byte ^ 0xff)
        self.short_be(port)
        return self

    def address_tuple(self, address: Tuple[str, int]) -> 'ByteWriter':
        return self.address(address[0], address[1])

    def to_bytes(self) -> bytes:
        return bytes(self._buffer)
