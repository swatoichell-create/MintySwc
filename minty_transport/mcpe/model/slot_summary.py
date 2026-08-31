
from dataclasses import dataclass

@dataclass
class SlotSummary:
    id: int
    count: int
    meta: int
    nbt_bytes: int
