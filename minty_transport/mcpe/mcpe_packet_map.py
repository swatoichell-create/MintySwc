
from .mcpe_packet_ids import McpePacketIds

class McpePacketMap:
    NEW_TO_OLD = {
        0x01: 0x8f,
        0x02: 0x90,
        0x05: 0x91,
        0x06: 0x92,
        0x07: 0x93,
        0x08: 0x94,
        0x09: 0x95,
        0x0a: 0x96,
        0x0b: 0x98,
        0x0c: 0x99,
        0x0d: 0x9a,
        0x0e: 0x9b,
        0x0f: 0x9c,
        0x10: 0x9d,
        0x12: 0x9e,
        0x13: 0x9f,
        0x14: 0xa0,
        0x15: 0xa1,
        0x16: 0xa2,
        0x17: 0xa3,
        0x18: 0xa4,
        0x19: 0xa5,
        0x1a: 0xa6,
        0x1b: 0xa7,
        0x1c: 0xa8,
        0x1e: 0xa9,
        0x1f: 0xaa,
        0x20: 0xab,
        0x21: 0xac,
        0x22: 0xad,
        0x23: 0xae,
        0x24: 0xaf,
        0x25: 0xb0,
        0x26: 0xb1,
        0x27: 0xb2,
        0x28: 0xb3,
        0x29: 0xb4,
        0x2a: 0xb5,
        0x2b: 0xb6,
        0x2c: 0xb7,
        0x2d: 0xb8,
        0x2e: 0xb9,
        0x2f: 0xba,
        0x30: 0xbb,
        0x31: 0xbc,
        0x32: 0xbd,
        0x33: 0xbe,
        0x34: 0xbf,
        0x35: 0xc0,
        0x36: 0xc1,
        0x37: 0xc2,
        0x38: 0xc3,
        0x39: 0xc4,
        0x3a: 0xc5,
        0x3b: 0xc6,
        0x3c: 0xc7,
        0x3d: 0xc8,
        0x3e: 0xc9,
        0x3f: 0xca,
        0x40: 0xcb,
    }

    OLD_TO_NEW = {old_id: new_id for new_id, old_id in NEW_TO_OLD.items()}

    @staticmethod
    def label(packet_id: int, new_protocol: bool) -> str:
        if new_protocol:
            return McpePacketMap._new_label(packet_id) or f"0x{packet_id:02x}"
        else:
            return McpePacketMap._old_label(packet_id) or f"0x{packet_id:02x}"

    @staticmethod
    def _new_label(packet_id: int) -> str:
        labels = {
            0x01: "LOGIN",
            0x02: "PLAY_STATUS",
            0x03: "SERVER_TO_CLIENT_HANDSHAKE",
            0x04: "CLIENT_TO_SERVER_HANDSHAKE",
            0x05: "DISCONNECT",
            0x06: "BATCH",
            0x07: "TEXT",
            0x08: "SET_TIME",
            0x09: "START_GAME",
            0x0a: "ADD_PLAYER",
            0x0b: "ADD_ENTITY",
            0x0f: "MOVE_ENTITY",
            0x10: "MOVE_PLAYER",
            0x12: "REMOVE_BLOCK",
            0x13: "UPDATE_BLOCK",
            0x1b: "MOB_EQUIPMENT",
            0x1c: "MOB_ARMOR_EQUIPMENT",
            0x1e: "INTERACT",
            0x1f: "USE_ITEM",
            0x20: "PLAYER_ACTION",
            0x23: "SET_ENTITY_MOTION",
            0x27: "ANIMATE",
            0x2c: "CONTAINER_SET_SLOT",
            0x38: "PLAYER_LIST",
            0x3d: "REQUEST_CHUNK_RADIUS",
        }
        return labels.get(packet_id)

    @staticmethod
    def _old_label(packet_id: int) -> str:
        labels = {
            0x8f: "LOGIN",
            0x90: "PLAY_STATUS",
            0x91: "DISCONNECT",
            0x92: "BATCH",
            0x93: "TEXT",
            0x94: "SET_TIME",
            0x95: "START_GAME",
            0x96: "ADD_PLAYER",
            0x97: "REMOVE_PLAYER",
            0x98: "ADD_ENTITY",
            0x9c: "MOVE_ENTITY",
            0x9d: "MOVE_PLAYER",
            0x9e: "REMOVE_BLOCK",
            0x9f: "UPDATE_BLOCK",
            0xa7: "MOB_EQUIPMENT",
            0xa8: "MOB_ARMOR_EQUIPMENT",
            0xa9: "INTERACT",
            0xaa: "USE_ITEM",
            0xab: "PLAYER_ACTION",
            0xae: "SET_ENTITY_MOTION",
            0xb2: "ANIMATE",
            0xb7: "CONTAINER_SET_SLOT",
            0xc8: "REQUEST_CHUNK_RADIUS",
            0xc9: "CHUNK_RADIUS_UPDATE",
        }
        return labels.get(packet_id)

    @staticmethod
    def label(id: int, new_protocol: bool) -> str:
        name = McpePacketMap._new_label(id) if new_protocol else McpePacketMap._old_label(id)
        if name is None:
            return f"0x{id:x}"
        return f"{name}/0x{id:x}"

    @staticmethod
    def _new_label(id: int):
        labels = {
            McpePacketIds.NEW_LOGIN: "LOGIN",
            0x02: "PLAY_STATUS",
            0x03: "SERVER_TO_CLIENT_HANDSHAKE",
            0x04: "CLIENT_TO_SERVER_HANDSHAKE",
            0x05: "DISCONNECT",
            McpePacketIds.NEW_BATCH: "BATCH",
            McpePacketIds.NEW_TEXT: "TEXT",
            0x08: "SET_TIME",
            0x09: "START_GAME",
            0x0a: "ADD_PLAYER",
            McpePacketIds.NEW_ADD_ENTITY: "ADD_ENTITY",
            McpePacketIds.NEW_MOVE_ENTITY: "MOVE_ENTITY",
            McpePacketIds.NEW_MOVE_PLAYER: "MOVE_PLAYER",
            McpePacketIds.NEW_REMOVE_BLOCK: "REMOVE_BLOCK",
            McpePacketIds.NEW_UPDATE_BLOCK: "UPDATE_BLOCK",
            McpePacketIds.NEW_MOB_EQUIPMENT: "MOB_EQUIPMENT",
            McpePacketIds.NEW_MOB_ARMOR_EQUIPMENT: "MOB_ARMOR_EQUIPMENT",
            0x1e: "INTERACT",
            McpePacketIds.NEW_USE_ITEM: "USE_ITEM",
            McpePacketIds.NEW_PLAYER_ACTION: "PLAYER_ACTION",
            McpePacketIds.NEW_SET_ENTITY_MOTION: "SET_ENTITY_MOTION",
            McpePacketIds.NEW_ANIMATE: "ANIMATE",
            McpePacketIds.NEW_CONTAINER_SET_SLOT: "CONTAINER_SET_SLOT",
            McpePacketIds.NEW_PLAYER_LIST: "PLAYER_LIST",
            McpePacketIds.NEW_REQUEST_CHUNK_RADIUS: "REQUEST_CHUNK_RADIUS",
        }
        return labels.get(id)

    @staticmethod
    def _old_label(id: int):
        labels = {
            McpePacketIds.OLD_LOGIN: "LOGIN",
            0x90: "PLAY_STATUS",
            0x91: "DISCONNECT",
            McpePacketIds.OLD_BATCH: "BATCH",
            McpePacketIds.OLD_TEXT: "TEXT",
            0x94: "SET_TIME",
            0x95: "START_GAME",
            0x96: "ADD_PLAYER",
            McpePacketIds.OLD_REMOVE_PLAYER: "REMOVE_PLAYER",
            McpePacketIds.OLD_ADD_ENTITY: "ADD_ENTITY",
            McpePacketIds.OLD_MOVE_ENTITY: "MOVE_ENTITY",
            0x9d: "MOVE_PLAYER",
            0x9e: "REMOVE_BLOCK",
            McpePacketIds.OLD_UPDATE_BLOCK: "UPDATE_BLOCK",
            0xa7: "MOB_EQUIPMENT",
            0xa8: "MOB_ARMOR_EQUIPMENT",
            0xa9: "INTERACT",
            0xaa: "USE_ITEM",
            0xab: "PLAYER_ACTION",
            McpePacketIds.OLD_SET_ENTITY_MOTION: "SET_ENTITY_MOTION",
            0xb2: "ANIMATE",
            0xb7: "CONTAINER_SET_SLOT",
            0xc8: "REQUEST_CHUNK_RADIUS",
            0xc9: "CHUNK_RADIUS_UPDATE",
        }
        return labels.get(id)
