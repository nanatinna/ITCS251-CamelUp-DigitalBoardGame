"""
betting.py - BetManager class handling leg bets and race bets.
"""
from typing import List, Dict, Optional, Tuple
from config.settings import CAMEL_COLORS

class BetManager:
    def __init__(self, players: List[str]):
        # 5, 3, 2, 1, 1 values for leg bets
        self.leg_tiles: Dict[str, List[int]] = {color: [5, 3, 2, 1, 1] for color in CAMEL_COLORS}
        
        self.active_leg_bets: List[Tuple[str, str, int]] = []
        
        self.race_bets: Dict[str, List[Tuple[str, str]]] = {
            "winner": [],
            "loser": []
        }
        
        self.player_race_bets: Dict[str, Dict[str, str]] = {p: {} for p in players}

    def place_leg_bet(self, player_name: str, camel_color: str) -> Optional[int]:
        if not self.leg_tiles[camel_color]:
            return None
        
        tile_val = self.leg_tiles[camel_color].pop(0)
        self.active_leg_bets.append((player_name, camel_color, tile_val))
        return tile_val

    def place_race_bet(self, player_name: str, camel_color: str, bet_type: str) -> bool:
        if bet_type not in ["winner", "loser"]:
            return False
            
        if bet_type in self.player_race_bets[player_name]:
            return False
            
        self.player_race_bets[player_name][bet_type] = camel_color
        self.race_bets[bet_type].append((player_name, camel_color))
        return True

    def reset_leg_bets(self):
        self.leg_tiles = {color: [5, 3, 2, 1, 1] for color in CAMEL_COLORS}
        self.active_leg_bets.clear()

    def resolve_leg(self, first_place_color: str, second_place_color: str) -> Dict[str, int]:
        payouts = {}
        
        for player, color, tile_val in self.active_leg_bets:
            if player not in payouts:
                payouts[player] = 0
                
            if color == first_place_color:
                payouts[player] += tile_val
            elif color == second_place_color:
                payouts[player] += 1
            else:
                payouts[player] -= 1
                
        return payouts

    def resolve_race(self, winner_color: str, loser_color: str) -> Dict[str, int]:
        payouts = {}
        payout_scale = [8, 5, 3, 2, 1]
        
        correct_winner_bets = 0
        for player, bet_color in self.race_bets["winner"]:
            if player not in payouts:
                payouts[player] = 0
            
            if bet_color == winner_color:
                award = payout_scale[correct_winner_bets] if correct_winner_bets < len(payout_scale) else 1
                payouts[player] += award
                correct_winner_bets += 1
            else:
                payouts[player] -= 1
                
        correct_loser_bets = 0
        for player, bet_color in self.race_bets["loser"]:
            if player not in payouts:
                payouts[player] = 0
            
            if bet_color == loser_color:
                award = payout_scale[correct_loser_bets] if correct_loser_bets < len(payout_scale) else 1
                payouts[player] += award
                correct_loser_bets += 1
            else:
                payouts[player] -= 1
                
        return payouts
