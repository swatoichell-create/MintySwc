
from typing import Dict
from .packet_translator import PacketTranslator
from .id_rewrite_packet_translator import IdRewritePacketTranslator
from .packet_direction import PacketDirection
from .mcpe_packet_map import McpePacketMap
from .mcpe_packet_ids import McpePacketIds
from .translator.login_translator import LoginTranslator
from .translator.client_batch_translator import ClientBatchTranslator
from .translator.text_translator import TextTranslator
from .translator.client_add_entity_translator import ClientAddEntityTranslator
from .translator.client_move_entity_translator import ClientMoveEntityTranslator

class ClientToServerRegistry:
    @staticmethod
    def build() -> Dict[int, PacketTranslator]:
        translators = {}
        for new_id, old_id in McpePacketMap.NEW_TO_OLD.items():
            translators[new_id] = IdRewritePacketTranslator(
                PacketDirection.CLIENT_TO_SERVER, new_id, old_id
            )
        translators[McpePacketIds.NEW_LOGIN] = LoginTranslator()
        translators[McpePacketIds.NEW_BATCH] = ClientBatchTranslator()
        translators[McpePacketIds.NEW_TEXT] = TextTranslator()
        translators[McpePacketIds.NEW_ADD_ENTITY] = ClientAddEntityTranslator()
        translators[McpePacketIds.NEW_MOVE_ENTITY] = ClientMoveEntityTranslator()
        return translators
