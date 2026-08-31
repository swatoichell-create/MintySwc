
from dataclasses import dataclass
from typing import List

@dataclass
class TextView:
    type: int
    source: str
    message: str
    parameters: List[str]
    remaining: int
