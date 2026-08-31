
import logging
from .mcpe_packet_ids import McpePacketIds
from .mcpe_bytes import McpeBytes
from ..util.byte_reader import ByteReader

class McpePacketInspector:
    DETAIL_LOG_FIRST = 24
    DETAIL_LOG_EVERY = 200

    def __init__(self):
        self.logger = logging.getLogger("minty_transport.mcpe.McpePacketInspector")
        self.move_detail_counter = 0
        self.action_detail_counter = 0
        self.use_item_detail_counter = 0
        self.inventory_detail_counter = 0

    def log_client_game_details(self, game: bytes):
        if not self.logger.isEnabledFor(logging.DEBUG) or not game:
            return

        try:
            packet_id = McpeBytes.packet_id(game)
            if packet_id == McpePacketIds.NEW_MOVE_PLAYER:
                if not self._should_log(self.move_detail_counter):
                    return
                reader = ByteReader(game, 1)
                entity_id = reader.long_be()
                x = reader.float_be()
                y = reader.float_be()
                z = reader.float_be()
                yaw = reader.float_be()
                head_yaw = reader.float_be()
                pitch = reader.float_be()
                mode = reader.u_byte()
                on_ground = reader.u_byte() != 0
                self.logger.debug(
                    f"C->S MOVE_PLAYER eid={entity_id} pos=({McpeBytes.fmt(x)}, {McpeBytes.fmt(y)}, {McpeBytes.fmt(z)}) "
                    f"rot=(yaw={McpeBytes.fmt(yaw)}, headYaw={McpeBytes.fmt(head_yaw)}, pitch={McpeBytes.fmt(pitch)}) "
                    f"mode={mode} onGround={on_ground} remaining={reader.remaining}"
                )
        except Exception as error:
            self.logger.debug(f"Unable to decode C->S packet detail: {error}")

    def _should_log(self, counter: int, first: int = DETAIL_LOG_FIRST, every: int = DETAIL_LOG_EVERY) -> bool:

        return True
