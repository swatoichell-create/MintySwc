
from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds

class UpdateBlockTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.SERVER_TO_CLIENT, McpePacketIds.OLD_UPDATE_BLOCK, McpePacketIds.NEW_UPDATE_BLOCK)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        return [self.rewrite_id(packet, self.target_id)]
