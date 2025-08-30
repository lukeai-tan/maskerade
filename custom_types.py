from dataclasses import dataclass


@dataclass
class CensorRegion:
    name: str
    bbox: tuple[int, int, int, int]
    is_censored: bool = False
