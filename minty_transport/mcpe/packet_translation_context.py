
from typing import Callable, List

class PacketTranslationContext:
    def __init__(
        self,
        translate_client_to_server: Callable[[bytes], List[bytes]],
        translate_server_to_client: Callable[[bytes], List[bytes]],
        record_drop: Callable[[int], None] = lambda id: None,
    ):
        self.translate_client_to_server = translate_client_to_server
        self.translate_server_to_client = translate_server_to_client
        self.record_drop = record_drop
