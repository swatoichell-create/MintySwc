
from ..util.byte_reader import ByteReader
from ..util.byte_writer import ByteWriter
from ..util.binary import Binary
from .mcpe_protocol import McpeProtocol
from .model.slot_summary import SlotSummary

class McpeBytes:
    @staticmethod
    def packet_id(game: bytes) -> int:
        return game[0] & 0xff if game else -1

    @staticmethod
    def strip_marker(payload: bytes, marker: int) -> bytes:
        if payload and (payload[0] & 0xff) == marker:
            return payload[1:]
        return payload

    @staticmethod
    def rewrite_game_id(game: bytes, id: int) -> bytes:
        return Binary.concat(bytes([id]), game[1:])

    @staticmethod
    def signed_byte(value: int) -> int:
        return value - 0x100 if value >= 0x80 else value

    @staticmethod
    def signed_short(value: int) -> int:
        return value - 0x10000 if value >= 0x8000 else value

    @staticmethod
    def angle_to_byte(degrees: float) -> int:
        return int(degrees / McpeProtocol.BYTE_ANGLE_UNIT) & 0xff

    @staticmethod
    def byte_angle_to_degrees(value: int) -> float:
        return (value & 0xff) * McpeProtocol.BYTE_ANGLE_UNIT

    @staticmethod
    def read_slot_summary(reader: ByteReader) -> SlotSummary:
        id_val = McpeBytes.signed_short(reader.short_be())
        if id_val <= 0:
            return SlotSummary(id=0, count=0, meta=0, nbt_bytes=0)

        count = reader.u_byte()
        meta = McpeBytes.signed_short(reader.short_be())
        nbt_bytes = reader.short_le()
        if nbt_bytes > 0:
            reader.skip(nbt_bytes)
        return SlotSummary(id=id_val, count=count, meta=meta, nbt_bytes=nbt_bytes)

    @staticmethod
    def fmt(value: float) -> str:
        return f"{value:.3f}"

    @staticmethod
    def shorten(value: str, max_length: int = 96) -> str:
        escaped = value.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n")
        return escaped if len(escaped) <= max_length else escaped[:max_length] + "..."
