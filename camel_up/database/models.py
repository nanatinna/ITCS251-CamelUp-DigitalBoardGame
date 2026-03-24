"""
models.py - Dataclasses for database records.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class GameRecord:
    id: Optional[int]
    started_at: str
    ended_at: Optional[str]
    winner_name: Optional[str]
    total_rounds: int
    player_count: int

@dataclass
class PlayerStats:
    name: str
    games_played: int
    games_won: int
    total_coins_earned: int
    best_score: int

@dataclass
class RoundRecord:
    id: Optional[int]
    game_id: int
    round_number: int
    camel_moved: str
    spaces_moved: int
    leg_ended: bool

@dataclass
class BetRecord:
    id: Optional[int]
    game_id: int
    player_id: int
    round_id: Optional[int]
    bet_type: str
    camel_color: str
    coins_won: int
