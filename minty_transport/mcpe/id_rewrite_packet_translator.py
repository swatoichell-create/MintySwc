
from typing import List
from .packet_translator import PacketTranslator
from .packet_direction import PacketDirection
from .packet_translation_context import PacketTranslationContext

class IdRewritePacketTranslator(PacketTranslator):
    def __init__(self, direction: PacketDirection, source_id: int, target_id: int):
        super().__init__(direction, source_id, target_id)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        return [self.rewrite_id(packet, self.target_id)]
