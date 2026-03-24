"""
dice.py - Pyramid class managing the dice.
"""
import random
from config.settings import CAMEL_COLORS
from typing import Optional, Tuple, List

class Pyramid:
    def __init__(self):
        self.remaining_dice: List[str] = []
        self.reset_leg()

    def reset_leg(self):
        """Prepares the pyramid for a new leg with all 5 dice."""
        self.remaining_dice = list(CAMEL_COLORS)
        random.shuffle(self.remaining_dice)

    def roll(self) -> Optional[Tuple[str, int]]:
        """Rolls a random remaining die (1-3). Returns (color, spaces)."""
        if not self.remaining_dice:
            return None
        
        color = self.remaining_dice.pop()
        spaces = random.randint(1, 3)
        return (color, spaces)

    def is_empty(self) -> bool:
        return len(self.remaining_dice) == 0
