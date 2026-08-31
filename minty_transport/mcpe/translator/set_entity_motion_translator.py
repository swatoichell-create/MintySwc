
from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds

class SetEntityMotionTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.SERVER_TO_CLIENT, McpePacketIds.OLD_SET_ENTITY_MOTION, McpePacketIds.NEW_SET_ENTITY_MOTION)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        return [self.rewrite_id(packet, self.target_id)]
