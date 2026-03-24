"""
player.py - Player dataclass.
"""
from dataclasses import dataclass, field
from typing import List

@dataclass
class Player:
    name: str
    coins: int = 3
    bet_history: List[str] = field(default_factory=list)
    has_placed_tile: bool = False
    tile_value: int = 0
    tile_space: int = -1
    
    def add_coins(self, amount: int):
        self.coins += amount
        if self.coins < 0:
            self.coins = 0
