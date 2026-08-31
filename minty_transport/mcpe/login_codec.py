import json
import logging
import base64
import random
from uuid import UUID
from .mcpe_protocol import McpeProtocol
from .model.login_data import LoginData
from ..util.byte_reader import ByteReader

class LoginCodec:
    logger = logging.getLogger("minty_transport.mcpe.LoginCodec")

    @staticmethod
    def parse_new_login(inflated: bytes) -> LoginData:
        reader = ByteReader(inflated)
        chain_json = reader.bytes(reader.int_le()).decode('utf-8')
        skin_token = reader.bytes(reader.int_le()).decode('utf-8') if reader.has_remaining() else ""

        username = "Player"
        uuid_val = UUID(bytes([0] * 16))
        client_secret = ""

        try:
            chain_root = json.loads(chain_json)
            chain = chain_root.get("chain", [])
            for element in chain:
                token = LoginCodec._decode_jwt_payload(element)
                if token:
                    extra_data = token.get("extraData", {})
                    if "displayName" in extra_data:
                        username = extra_data["displayName"]
                    if "identity" in extra_data:
                        uuid_val = UUID(extra_data["identity"])
                    if "identityPublicKey" in token:
                        client_secret = token["identityPublicKey"]
        except Exception as e:
            LoginCodec.logger.debug(f"Unable to decode chain JSON: {e}")

        skin_token_data = LoginCodec._decode_jwt_payload(skin_token) or {}
        client_id = skin_token_data.get("ClientRandomId", random.getrandbits(64))
        server_address = skin_token_data.get("ServerAddress", "")
        skin_model = skin_token_data.get("SkinId", "Standard_Steve")
        skin_data_base64 = skin_token_data.get("SkinData", "")

        try:
            skin_data = base64.b64decode(skin_data_base64)
            if len(skin_data) not in [McpeProtocol.SINGLE_SKIN_SIZE, McpeProtocol.DOUBLE_SKIN_SIZE]:
                skin_data = bytes(McpeProtocol.SINGLE_SKIN_SIZE)
        except Exception:
            skin_data = bytes(McpeProtocol.SINGLE_SKIN_SIZE)

        return LoginData(
            username=username,
            client_uuid=uuid_val,
            client_id=client_id,
            client_secret=client_secret,
            server_address=server_address,
            skin_model=skin_model,
            skin_data=skin_data,
        )

    @staticmethod
    def _decode_jwt_payload(token: str):
        try:
            parts = token.split('.')
            if len(parts) < 2:
                return None
            payload = parts[1]
            padded = payload + '=' * ((4 - len(payload) % 4) % 4)
            decoded = base64.urlsafe_b64decode(padded)
            return json.loads(decoded.decode('utf-8'))
        except Exception as e:
            LoginCodec.logger.debug(f"Unable to decode JWT payload: {e}")
            return None
