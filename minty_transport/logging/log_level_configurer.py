
import logging
from typing import Optional

class LogLevelConfigurer:
    ROOT_LOGGER = "minty_transport"

    @staticmethod
    def apply(configured_level: str):
        logger = logging.getLogger(LogLevelConfigurer.ROOT_LOGGER)
        level = LogLevelConfigurer._parse_level(configured_level.strip().upper())
        if level is None:
            logger.warning(f"Unknown logLevel '{configured_level}', falling back to INFO")
            level = logging.INFO

        logger.setLevel(level)
        logger.info(f"Log level set to {logging.getLevelName(level)}")

    @staticmethod
    def _parse_level(level_str: str) -> Optional[int]:
        level_map = {
            "OFF": logging.CRITICAL + 1,
            "ERROR": logging.ERROR,
            "WARN": logging.WARNING,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "TRACE": logging.DEBUG - 5,
        }
        return level_map.get(level_str)
