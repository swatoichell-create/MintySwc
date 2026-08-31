
from abc import ABC, abstractmethod
from typing import List
from ..util.binary import Binary
from .packet_direction import PacketDirection
from .packet_translation_context import PacketTranslationContext

class PacketTranslator(ABC):
    def __init__(self, direction: PacketDirection, source_id: int, target_id: int):
        self.direction = direction
        self.source_id = source_id
        self.target_id = target_id

    @abstractmethod
    def translate(self, packet: bytes, context: PacketTranslationContext) -> List[bytes]:
        pass

    def rewrite_id(self, packet: bytes, id: int) -> bytes:
        return Binary.concat(bytes([id]), packet[1:])
