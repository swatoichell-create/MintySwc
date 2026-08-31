from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ...util.byte_reader import ByteReader
from ...util.byte_writer import ByteWriter

class UpdateBlockTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.SERVER_TO_CLIENT, McpePacketIds.OLD_UPDATE_BLOCK, McpePacketIds.NEW_UPDATE_BLOCK)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        reader = ByteReader(packet, 1)
        count = reader.int_be()
        if count <= 0:
            return []

        writer = ByteWriter()
        writer.byte(McpePacketIds.NEW_UPDATE_BLOCK)
        for _ in range(count):
            writer.bytes(reader.bytes(11))

        return [writer.to_bytes()]
