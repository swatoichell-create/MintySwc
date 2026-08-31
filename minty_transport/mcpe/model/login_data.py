
from dataclasses import dataclass
from uuid import UUID

@dataclass
class LoginData:
    username: str
    client_uuid: UUID
    client_id: int
    client_secret: str
    server_address: str
    skin_model: str
    skin_data: bytes
