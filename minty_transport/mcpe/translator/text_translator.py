from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ..mcpe_bytes import McpeBytes
from ..text_type import TextType
from ..model.text_view import TextView
from ...util.byte_reader import ByteReader
from ...util.byte_writer import ByteWriter
import logging

class TextTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.CLIENT_TO_SERVER, McpePacketIds.NEW_TEXT, McpePacketIds.OLD_TEXT)
        self.logger = logging.getLogger("minty_transport.mcpe.translator.TextTranslator")

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        text = self._parse_text(packet)
        if text is None:
            self.logger.debug(f"C->S TEXT decode failed, falling back to id rewrite; len={len(packet)}")
            return [McpeBytes.rewrite_game_id(packet, self.target_id)]

        self.logger.debug(
            f"C->S TEXT type={text.type} source='{McpeBytes.shorten(text.source)}' "
            f"message='{McpeBytes.shorten(text.message)}' params={len(text.parameters)} remaining={text.remaining}"
        )

        if text.type in [TextType.RAW, TextType.CHAT]:
            writer = ByteWriter()
            writer.byte(McpePacketIds.OLD_TEXT)
            writer.byte(TextType.CHAT)
            writer.string_be("")
            writer.string_be(text.message)
            return [writer.to_bytes()]

        return [McpeBytes.rewrite_game_id(packet, self.target_id)]

    def _parse_text(self, game: bytes) -> TextView:
        try:
            reader = ByteReader(game, 1)
            text_type = reader.u_byte()
            source = ""
            message = ""
            parameters = []

            if text_type in [TextType.POPUP, TextType.CHAT]:
                source = reader.string_be()
                message = reader.string_be()
            elif text_type in [TextType.RAW, TextType.TIP, TextType.SYSTEM]:
                message = reader.string_be()
            elif text_type == TextType.TRANSLATION:
                message = reader.string_be()
                count = reader.u_byte()
                for _ in range(count):
                    parameters.append(reader.string_be())

            return TextView(text_type, source, message, parameters, reader.remaining)
        except Exception as e:
            self.logger.debug(f"Failed to parse TEXT packet: {e}")
            return None
