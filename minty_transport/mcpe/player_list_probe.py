
import logging
from .mcpe_bytes import McpeBytes
from .mcpe_packet_ids import McpePacketIds
from .mcpe_protocol import McpeProtocol
from ..util.byte_reader import ByteReader

class PlayerListProbe:
    @staticmethod
    def already_new_server_game_or_none(game: bytes):
        packet_id = McpeBytes.packet_id(game)
        if packet_id == McpePacketIds.NEW_PLAYER_LIST and PlayerListProbe._looks_like_player_list(game):
            logger = logging.getLogger("minty_transport.mcpe.PlayerListProbe")
            logger.debug(f"Passing through already-new S->C PLAYER_LIST")
            return game
        return None

    @staticmethod
    def _looks_like_player_list(game: bytes) -> bool:
        if len(game) < 6:
            return False
        type_val = game[1] & 0xff
        if type_val != 0 and type_val != McpeProtocol.PLAYER_LIST_REMOVE:
            return False
        count = ByteReader(game, 2).int_be()
        if count < 0 or count > 2048:
            return False
        if type_val == McpeProtocol.PLAYER_LIST_REMOVE:
            return len(game) == 6 + count * 16
        else:
            return len(game) >= 6 + count * 30
