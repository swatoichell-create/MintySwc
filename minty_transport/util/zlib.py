
import zlib

class Zlib:
    @staticmethod
    def deflate(data: bytes, level: int = zlib.Z_DEFAULT_COMPRESSION) -> bytes:
        compressor = zlib.compressobj(level)
        return compressor.compress(data) + compressor.flush()

    @staticmethod
    def inflate(data: bytes, max_size: int = 64 * 1024 * 1024) -> bytes:
        decompressor = zlib.decompressobj()
        result = decompressor.decompress(data, max_size)
        if decompressor.unused_data:
            raise ValueError("Extra data after decompression")
        return result
