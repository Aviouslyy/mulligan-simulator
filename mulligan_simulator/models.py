"""
Data models for the mulligan simulator.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class HandResult:
    """Result of a single hand simulation."""
    hand_number: int
    seed: int
    cards_in_hand: int
    cards: List[str]
    play_or_draw: str  # "play" or "draw"
    mulligan_number: int  # 1 for 7 cards, 2 for 6, etc.
    user_decision: str  # "keep" or "mulligan"
    cards_to_keep: Optional[List[str]] = None
    timestamp: str = ""
