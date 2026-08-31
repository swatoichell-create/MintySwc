from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ..mcpe_protocol import McpeProtocol
from ...util.byte_reader import ByteReader
from ...util.byte_writer import ByteWriter

class RemovePlayerTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.SERVER_TO_CLIENT, McpePacketIds.OLD_REMOVE_PLAYER, McpePacketIds.NEW_PLAYER_LIST)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        reader = ByteReader(packet, 1)
        entity_id = reader.long_be()
        uuid_val = reader.uuid()

        player_list_remove = ByteWriter()
        player_list_remove.byte(McpePacketIds.NEW_PLAYER_LIST)
        player_list_remove.byte(McpeProtocol.PLAYER_LIST_REMOVE)
        player_list_remove.int_be(1)
        player_list_remove.uuid(uuid_val)

        remove_entity = ByteWriter()
        remove_entity.byte(McpePacketIds.NEW_REMOVE_ENTITY)
        remove_entity.long_be(entity_id)

        return [player_list_remove.to_bytes(), remove_entity.to_bytes()]
