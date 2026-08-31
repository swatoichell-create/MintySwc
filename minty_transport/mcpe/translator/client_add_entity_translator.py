from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ..mcpe_protocol import McpeProtocol
from ...util.byte_reader import ByteReader
from ...util.byte_writer import ByteWriter

class ClientAddEntityTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.CLIENT_TO_SERVER, McpePacketIds.NEW_ADD_ENTITY, McpePacketIds.OLD_ADD_ENTITY)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        reader = ByteReader(packet, 1)
        entity_id = reader.long_be()
        entity_type = reader.int_be()
        x = reader.float_be()
        y = reader.float_be()
        z = reader.float_be()
        speed_x = reader.float_be()
        speed_y = reader.float_be()
        speed_z = reader.float_be()
        yaw = reader.float_be()
        pitch = reader.float_be()
        reader.int_be()
        metadata_and_links = reader.bytes(reader.remaining)

        writer = ByteWriter()
        writer.byte(McpePacketIds.OLD_ADD_ENTITY)
        writer.long_be(entity_id)
        writer.int_be(entity_type)
        writer.float_be(x)
        writer.float_be(y)
        writer.float_be(z)
        writer.float_be(speed_x)
        writer.float_be(speed_y)
        writer.float_be(speed_z)
        writer.float_be(yaw / McpeProtocol.ADD_ENTITY_ROTATION_SCALE)
        writer.float_be(pitch / McpeProtocol.ADD_ENTITY_ROTATION_SCALE)
        writer.bytes(metadata_and_links)

        return [writer.to_bytes()]
