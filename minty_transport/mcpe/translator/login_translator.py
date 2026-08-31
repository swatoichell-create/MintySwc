from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ..mcpe_protocol import McpeProtocol
from ..login_codec import LoginCodec
from ...util.byte_reader import ByteReader
from ...util.byte_writer import ByteWriter
from ...util.zlib import Zlib
import logging

class LoginTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.CLIENT_TO_SERVER, McpePacketIds.NEW_LOGIN, McpePacketIds.OLD_LOGIN)
        self.logger = logging.getLogger("minty_transport.mcpe.translator.LoginTranslator")

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        return [self._encode_old_login_game(packet)]

    def _encode_old_login_game(self, new_game: bytes) -> bytes:
        reader = ByteReader(new_game, 1)
        protocol = reader.int_be()
        if protocol != McpeProtocol.NEW_PROTOCOL:
            self.logger.debug(f"Client login protocol is {protocol}, expected {McpeProtocol.NEW_PROTOCOL}")

        compressed = reader.bytes(reader.int_be())
        login = LoginCodec.parse_new_login(Zlib.inflate(compressed))

        writer = ByteWriter()
        writer.byte(McpePacketIds.OLD_LOGIN)
        writer.string_be(login.username)
        writer.int_be(McpeProtocol.OLD_PROTOCOL)
        writer.int_be(McpeProtocol.OLD_PROTOCOL)
        writer.long_be(login.client_id)
        writer.uuid(login.client_uuid)
        writer.string_be(login.server_address)
        writer.string_be(login.client_secret)
        writer.string_be(login.skin_model)
        writer.short_be(len(login.skin_data))
        writer.bytes(login.skin_data)

        encoded = writer.to_bytes()
        self.logger.info(
            f"Translated login {login.username} ({login.client_uuid}) from protocol {protocol} to {McpeProtocol.OLD_PROTOCOL}; "
            f"oldLen={len(encoded) + 1} skinBytes={len(login.skin_data)} secretBytes={len(login.client_secret.encode('utf-8'))}"
        )
        return encoded
