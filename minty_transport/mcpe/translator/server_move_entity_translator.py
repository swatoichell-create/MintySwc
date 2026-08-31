from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ..mcpe_bytes import McpeBytes
from ...util.byte_reader import ByteReader
from ...util.byte_writer import ByteWriter

class ServerMoveEntityTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.SERVER_TO_CLIENT, McpePacketIds.OLD_MOVE_ENTITY, McpePacketIds.NEW_MOVE_ENTITY)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        reader = ByteReader(packet, 1)
        count = reader.int_be()
        if count <= 0:
            return []

        new_games = []
        for _ in range(count):
            entity_id = reader.long_be()
            x = reader.float_be()
            y = reader.float_be()
            z = reader.float_be()
            yaw = reader.float_be()
            head_yaw = reader.float_be()
            pitch = reader.float_be()

            writer = ByteWriter()
            writer.byte(McpePacketIds.NEW_MOVE_ENTITY)
            writer.long_be(entity_id)
            writer.float_be(x)
            writer.float_be(y)
            writer.float_be(z)
            writer.byte(McpeBytes.angle_to_byte(pitch))
            writer.byte(McpeBytes.angle_to_byte(head_yaw))
            writer.byte(McpeBytes.angle_to_byte(yaw))
            new_games.append(writer.to_bytes())

        return new_games
