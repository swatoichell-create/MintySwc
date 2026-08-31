
import json
import os
from pathlib import Path
from typing import Dict, Any
from .proxy_config import ProxyConfig

class ConfigLoader:
    @staticmethod
    def load(path: Path) -> ProxyConfig:
        if not path.exists():
            default_config = ProxyConfig()
            parent = path.parent
            if parent != Path("."):
                parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(ConfigLoader._to_dict(default_config), f, indent=2)
            return default_config

        with open(path, "r") as f:
            data = json.load(f)
            return ConfigLoader._from_dict(data)

    @staticmethod
    def _to_dict(config: ProxyConfig) -> Dict[str, Any]:
        return {
            "localServerAddress": config.local_server_address,
            "targetServerAddress": config.target_server_address,
            "logLevel": config.log_level,
        }

    @staticmethod
    def _from_dict(data: Dict[str, Any]) -> ProxyConfig:
        return ProxyConfig(
            local_server_address=data.get("localServerAddress", "0.0.0.0:19132"),
            target_server_address=data.get("targetServerAddress", "0.0.0.0:19133"),
            log_level=data.get("logLevel", "INFO"),
        )
