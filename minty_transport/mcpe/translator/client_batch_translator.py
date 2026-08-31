
from typing import List
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..packet_translation_context import PacketTranslationContext
from ..mcpe_packet_ids import McpePacketIds
from ..mcpe_bytes import McpeBytes
from ...util.byte_reader import ByteReader
from ...util.zlib import Zlib

class ClientBatchTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.CLIENT_TO_SERVER, McpePacketIds.NEW_BATCH, McpePacketIds.OLD_BATCH)

    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        reader = ByteReader(packet)
        reader.skip(1)

        compressed = reader.byte()
        data_len = reader.int_be()

        if compressed == 0:

            data = reader.bytes(data_len)
        else:

            compressed_data = reader.bytes(data_len)
            data = Zlib.inflate(compressed_data)

        packets = self._split_packets(data)
        translated_packets = []
        for pkt in packets:
            for translated in context.translate_client_to_server(pkt):
                translated_packets.append(translated)

        return [self._build_batch(translated_packets)]

    def _split_packets(self, data: bytes) -> List[bytes]:
        packets = []
        offset = 0
        while offset < len(data):
            if offset + 4 > len(data):
                break
            length = int.from_bytes(data[offset:offset+4], byteorder='little')
            offset += 4
            if offset + length > len(data):
                break
            packets.append(data[offset:offset+length])
            offset += length
        return packets

    def _build_batch(self, packets: List[bytes]) -> bytes:
        builder = bytearray()
        builder.append(McpePacketIds.OLD_BATCH)
        builder.append(0)
        data_builder = bytearray()
        for pkt in packets:
            data_builder.extend(len(pkt).to_bytes(4, byteorder='little'))
            data_builder.extend(pkt)
        builder.extend(len(data_builder).to_bytes(4, byteorder='big'))
        builder.extend(data_builder)
        return bytes(builder)
