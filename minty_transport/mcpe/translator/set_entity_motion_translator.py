from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ...util.byte_reader import ByteReader
from ...util.byte_writer import ByteWriter

class SetEntityMotionTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.SERVER_TO_CLIENT, McpePacketIds.OLD_SET_ENTITY_MOTION, McpePacketIds.NEW_SET_ENTITY_MOTION)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        reader = ByteReader(packet, 1)
        count = reader.int_be()
        if count <= 0:
            return []

        writer = ByteWriter()
        writer.byte(McpePacketIds.NEW_SET_ENTITY_MOTION)
        for _ in range(count):
            writer.long_be(reader.long_be())
            writer.float_be(reader.float_be())
            writer.float_be(reader.float_be())
            writer.float_be(reader.float_be())

        return [writer.to_bytes()]
