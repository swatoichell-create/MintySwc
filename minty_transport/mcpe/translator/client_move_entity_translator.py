from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ..mcpe_bytes import McpeBytes
from ...util.byte_reader import ByteReader
from ...util.byte_writer import ByteWriter

class ClientMoveEntityTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.CLIENT_TO_SERVER, McpePacketIds.NEW_MOVE_ENTITY, McpePacketIds.OLD_MOVE_ENTITY)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        reader = ByteReader(packet, 1)
        entity_id = reader.long_be()
        x = reader.float_be()
        y = reader.float_be()
        z = reader.float_be()
        pitch = McpeBytes.byte_angle_to_degrees(reader.u_byte())
        head_yaw = McpeBytes.byte_angle_to_degrees(reader.u_byte())
        yaw = McpeBytes.byte_angle_to_degrees(reader.u_byte())

        writer = ByteWriter()
        writer.byte(McpePacketIds.OLD_MOVE_ENTITY)
        writer.int_be(1)
        writer.long_be(entity_id)
        writer.float_be(x)
        writer.float_be(y)
        writer.float_be(z)
        writer.float_be(yaw)
        writer.float_be(head_yaw)
        writer.float_be(pitch)

        return [writer.to_bytes()]
