from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ..mcpe_protocol import McpeProtocol
from ..mcpe_bytes import McpeBytes
from ..batch_codec import BatchCodec
from ...util.byte_writer import ByteWriter
from ...util.zlib import Zlib
from ...util.binary import Binary

class ServerBatchTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.SERVER_TO_CLIENT, McpePacketIds.OLD_BATCH, McpePacketIds.NEW_BATCH)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        inflated = Zlib.inflate(BatchCodec.read_batch_payload(packet))
        out = ByteWriter()

        def process_old_marked(old_marked):
            old_inner = McpeBytes.strip_marker(old_marked, McpeProtocol.OLD_MARKER)
            for new_game in context.translate_server_to_client(old_inner):
                out.int_be(len(new_game))
                out.bytes(new_game)

        BatchCodec.for_each_batch_packet(inflated, process_old_marked)

        deflated = Zlib.deflate(out.to_bytes(), level=1)
        return [
            Binary.concat(
                bytes([McpePacketIds.NEW_BATCH]),
                Binary.int_be(len(deflated)),
                deflated
            )
        ]
