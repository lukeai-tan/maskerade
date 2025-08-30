# Maskerade: AI-powered privacy filter for faces & sensitive information
# (c) 2025 Team Breaking Byte. All rights reserved.
#
# This software was developed as part of Tiktok Techjam 2025, August 2025.
# You may use, modify, and distribute this code for non-commercial hackathon and educational purposes.
# For other uses, please contact the author(s).

from dataclasses import dataclass


@dataclass
class CensorRegion:
    name: str
    bbox: tuple[int, int, int, int]
    is_censored: bool = False
