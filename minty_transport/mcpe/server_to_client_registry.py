
from typing import Dict
from .packet_translator import PacketTranslator
from .id_rewrite_packet_translator import IdRewritePacketTranslator
from .packet_direction import PacketDirection
from .mcpe_packet_map import McpePacketMap
from .mcpe_packet_ids import McpePacketIds
from .translator.server_batch_translator import ServerBatchTranslator
from .translator.remove_player_translator import RemovePlayerTranslator
from .translator.server_add_entity_translator import ServerAddEntityTranslator
from .translator.server_move_entity_translator import ServerMoveEntityTranslator
from .translator.update_block_translator import UpdateBlockTranslator
from .translator.set_entity_motion_translator import SetEntityMotionTranslator

class ServerToClientRegistry:
    @staticmethod
    def build() -> Dict[int, PacketTranslator]:
        translators = {}
        for old_id, new_id in McpePacketMap.OLD_TO_NEW.items():
            translators[old_id] = IdRewritePacketTranslator(
                PacketDirection.SERVER_TO_CLIENT, old_id, new_id
            )
        translators[McpePacketIds.OLD_BATCH] = ServerBatchTranslator()
        translators[McpePacketIds.OLD_REMOVE_PLAYER] = RemovePlayerTranslator()
        translators[McpePacketIds.OLD_ADD_ENTITY] = ServerAddEntityTranslator()
        translators[McpePacketIds.OLD_MOVE_ENTITY] = ServerMoveEntityTranslator()
        translators[McpePacketIds.OLD_UPDATE_BLOCK] = UpdateBlockTranslator()
        translators[McpePacketIds.OLD_SET_ENTITY_MOTION] = SetEntityMotionTranslator()
        return translators
