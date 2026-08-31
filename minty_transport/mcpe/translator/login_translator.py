
from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ..mcpe_protocol import McpeProtocol
from ..mcpe_bytes import McpeBytes
from ...util.byte_reader import ByteReader
from ...util.byte_writer import ByteWriter
from ...util.binary import Binary

class LoginTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.CLIENT_TO_SERVER, McpePacketIds.NEW_LOGIN, McpePacketIds.OLD_LOGIN)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        reader = ByteReader(packet)
        reader.skip(1)

        protocol = reader.int_be()
        if protocol != McpeProtocol.NEW_PROTOCOL:
            return []

        writer = ByteWriter()
        writer.byte(McpePacketIds.OLD_LOGIN)
        writer.int_be(McpeProtocol.OLD_PROTOCOL)

        writer.bytes(reader.bytes(reader.remaining))

        return [writer.to_bytes()]
