"""
camel.py - Camel dataclass for the game board.
"""
from dataclasses import dataclass

@dataclass
class Camel:
    color: str
    position: int = 0
    stack_order: int = 0
