from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ..mcpe_protocol import McpeProtocol
from ..mcpe_bytes import McpeBytes
from ..batch_codec import BatchCodec
from ...util.zlib import Zlib
import logging

class ClientBatchTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.CLIENT_TO_SERVER, McpePacketIds.NEW_BATCH, McpePacketIds.OLD_BATCH)
        self.logger = logging.getLogger("minty_transport.mcpe.translator.ClientBatchTranslator")

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        inflated = Zlib.inflate(BatchCodec.read_batch_payload(packet))
        translated_packets = []

        def process_inner_game(inner_new_game):
            new_game = McpeBytes.strip_marker(inner_new_game, McpeProtocol.NEW_MARKER)
            translated_packets.extend(context.translate_client_to_server(new_game))

        BatchCodec.for_each_batch_packet(inflated, process_inner_game)

        if not translated_packets:
            return []

        self.logger.debug(f"C->S batch unbatched into {len(translated_packets)} direct 0.14 packet(s)")
        return translated_packets
