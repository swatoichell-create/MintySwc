import logging
from ..util.byte_reader import ByteReader

class BatchCodec:
    logger = logging.getLogger("minty_transport.mcpe.BatchCodec")

    @staticmethod
    def read_batch_payload(game: bytes) -> bytes:
        reader = ByteReader(game, 1)
        length = reader.int_be()
        return reader.bytes(length)

    @staticmethod
    def for_each_batch_packet(inflated: bytes, consumer):
        reader = ByteReader(inflated)
        while reader.has_remaining():
            length = reader.int_be()
            if length <= 0 or length > reader.remaining:
                BatchCodec.logger.debug(f"Stopping malformed Batch payload at length {length}")
                return
            consumer(reader.bytes(length))
