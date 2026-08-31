
from dataclasses import dataclass

@dataclass
class ProxyConfig:
    local_server_address: str = "0.0.0.0:19132"
    target_server_address: str = "0.0.0.0:19133"
    log_level: str = "INFO"
