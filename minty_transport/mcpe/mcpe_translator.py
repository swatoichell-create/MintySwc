
import logging
from typing import List, Callable
from .mcpe_bytes import McpeBytes
from .mcpe_protocol import McpeProtocol
from .mcpe_packet_ids import McpePacketIds
from .mcpe_packet_map import McpePacketMap
from .packet_translation_context import PacketTranslationContext
from .client_to_server_registry import ClientToServerRegistry
from .server_to_client_registry import ServerToClientRegistry
from .player_list_probe import PlayerListProbe
from ..util.binary import Binary

class McpeTranslator:
    logger = logging.getLogger("minty_transport.mcpe.McpeTranslator")

    CLIENT_TO_SERVER_TRANSLATORS = ClientToServerRegistry.build()
    SERVER_TO_CLIENT_TRANSLATORS = ServerToClientRegistry.build()

    @staticmethod
    def client_to_server(
        payload: bytes,
        inspector,
        record_drop: Callable[[int], None] = lambda id: None,
    ) -> List[bytes]:
        try:
            context = McpeTranslator._client_context(inspector, record_drop)
            game = McpeBytes.strip_marker(payload, McpeProtocol.NEW_MARKER)
            translated = McpeTranslator._new_game_to_old_games(game, context, inspector)
            translated_marked = [McpeTranslator._mark_old(pkt) for pkt in translated]

            if McpeTranslator.logger.isEnabledFor(logging.DEBUG) and game:
                packet_id = McpeBytes.packet_id(game)
                McpeTranslator.logger.debug(
                    f"C->S MCPE 0.15 {McpePacketMap.label(packet_id, new_protocol=True)} len={len(game)} -> "
                    f"{[f'{McpePacketMap.label(McpeBytes.packet_id(McpeBytes.strip_marker(pkt, McpeProtocol.OLD_MARKER)), new_protocol=False)}/len={len(pkt)}' for pkt in translated_marked]}"
                )

            return translated_marked
        except Exception as e:
            McpeTranslator.logger.warning(f"Failed to translate client packet: {e}")
            return []

    @staticmethod
    def server_to_client(
        payload: bytes,
        record_drop: Callable[[int], None] = lambda id: None,
    ) -> List[bytes]:
        try:
            context = McpeTranslator._server_context(record_drop)
            old_game = McpeBytes.strip_marker(payload, McpeProtocol.OLD_MARKER)
            new_games = McpeTranslator._old_game_to_new_games(old_game, context)

            if McpeTranslator.logger.isEnabledFor(logging.DEBUG) and old_game:
                packet_id = McpeBytes.packet_id(old_game)
                McpeTranslator.logger.debug(
                    f"S->C MCPE 0.14 {McpePacketMap.label(packet_id, new_protocol=False)} len={len(old_game)} -> "
                    f"{[f'{McpePacketMap.label(McpeBytes.packet_id(pkt), new_protocol=True)}/len={len(pkt)}' for pkt in new_games]}"
                )

            return [Binary.concat(bytes([McpeProtocol.NEW_MARKER]), game) for game in new_games]
        except Exception as e:
            McpeTranslator.logger.warning(f"Failed to translate server packet: {e}")
            return []

    @staticmethod
    def _client_context(inspector, record_drop: Callable[[int], None]) -> PacketTranslationContext:
        def translate_client_to_server(game: bytes) -> List[bytes]:
            return McpeTranslator._new_game_to_old_games(game, context, inspector)

        def translate_server_to_client(game: bytes) -> List[bytes]:
            return McpeTranslator._old_game_to_new_games(game, context)

        context = PacketTranslationContext(
            translate_client_to_server=translate_client_to_server,
            translate_server_to_client=translate_server_to_client,
            record_drop=record_drop,
        )
        return context

    @staticmethod
    def _server_context(record_drop: Callable[[int], None]) -> PacketTranslationContext:
        def translate_client_to_server(game: bytes) -> List[bytes]:
            return McpeTranslator._new_game_to_old_games(game, context, inspector=None)

        def translate_server_to_client(game: bytes) -> List[bytes]:
            return McpeTranslator._old_game_to_new_games(game, context)

        context = PacketTranslationContext(
            translate_client_to_server=translate_client_to_server,
            translate_server_to_client=translate_server_to_client,
            record_drop=record_drop,
        )
        return context

    @staticmethod
    def _new_game_to_old_games(game: bytes, context: PacketTranslationContext, inspector) -> List[bytes]:
        if not game:
            return []
        packet_id = McpeBytes.packet_id(game)
        if packet_id != McpePacketIds.NEW_BATCH:
            if inspector:
                inspector.log_client_game_details(game)

        translator = McpeTranslator.CLIENT_TO_SERVER_TRANSLATORS.get(packet_id)
        if translator is None:
            context.record_drop(packet_id)
            McpeTranslator.logger.debug(f"Dropping unsupported 0.15.10 packet id 0x{packet_id:x}")
            return []
        return translator.translate(game, context)

    @staticmethod
    def _old_game_to_new_games(game: bytes, context: PacketTranslationContext) -> List[bytes]:
        old_game = McpeBytes.strip_marker(game, McpeProtocol.OLD_MARKER)
        if not old_game:
            return []
        packet_id = McpeBytes.packet_id(old_game)
        translator = McpeTranslator.SERVER_TO_CLIENT_TRANSLATORS.get(packet_id)
        if translator is None:
            already_new = PlayerListProbe.already_new_server_game_or_none(old_game)
            if already_new is not None:
                return [already_new]
            context.record_drop(packet_id)
            McpeTranslator.logger.debug(f"Dropping unsupported 0.14.3 packet id 0x{packet_id:x}")
            return []
        return translator.translate(old_game, context)

    @staticmethod
    def _mark_old(game: bytes) -> bytes:
        return Binary.concat(bytes([McpeProtocol.OLD_MARKER]), game)
