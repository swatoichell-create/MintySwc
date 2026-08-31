
from typing import List
from .byte_writer import ByteWriter

class Binary:
    @staticmethod
    def concat(*parts: bytes) -> bytes:
        return b"".join(parts)

    @staticmethod
    def int_be(value: int) -> bytes:
        return ByteWriter().int_be(value).to_bytes()

    @staticmethod
    def short_be(value: int) -> bytes:
        return ByteWriter().short_be(value).to_bytes()

    @staticmethod
    def l_triad(value: int) -> bytes:
        return ByteWriter().l_triad(value).to_bytes()

    @staticmethod
    def split_bytes(data: bytes, chunk_size: int) -> List[bytes]:
        if chunk_size <= 0:
            raise ValueError("chunkSize must be positive")
        if not data:
            return [b""]
        chunks = []
        offset = 0
        while offset < len(data):
            end = min(offset + chunk_size, len(data))
            chunks.append(data[offset:end])
            offset = end
        return chunks
