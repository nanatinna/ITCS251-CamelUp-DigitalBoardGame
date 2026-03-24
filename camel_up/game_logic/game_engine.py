"""
game_engine.py - GameEngine class orchestrating the full game loop.
"""
from typing import List, Dict, Tuple, Optional
from config.settings import CAMEL_COLORS
from .camel import Camel
from .board import Board
from .dice import Pyramid
from .player import Player
from .betting import BetManager
import random

class GameEngine:
    def __init__(self, db_manager):
        self.db = db_manager
        self.board = Board()
        self.pyramid = Pyramid()
        self.players: List[Player] = []
        self.bet_manager: Optional[BetManager] = None
        self.current_player_idx = 0
        
        self.game_id = -1
        self.round_number = 1
        self.is_race_over = False
        self.event_queue: List[dict] = []

    def start_game(self, player_names: List[str]):
        """Initializes board, camels, dice, players."""
        self.players = [Player(name) for name in player_names]
        self.bet_manager = BetManager(player_names)
        self.current_player_idx = 0
        
        init_positions = {}
        temp_pyramid = Pyramid()
        while not temp_pyramid.is_empty():
            res = temp_pyramid.roll()
            if res:
                color, spaces = res
                init_positions[color] = spaces
            
        self.board.setup_camels(init_positions)
        self.pyramid.reset_leg()
        self.is_race_over = False
        self.round_number = 1
        self.event_queue.clear()
        
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.game_id = self.db.save_game_start(now, len(player_names), player_names)

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    def available_actions(self) -> List[str]:
        actions = ["roll"]
        actions.append("place_tile")
        
        for color in CAMEL_COLORS:
            if self.bet_manager and self.bet_manager.leg_tiles[color]:
                actions.append("leg_bet")
                break
                
        actions.append("race_bet")
        return actions

    def do_roll(self) -> Optional[Tuple[str, int]]:
        if self.pyramid.is_empty() or self.is_race_over:
            return None
            
        result = self.pyramid.roll()
        if not result:
            return None
            
        color, spaces = result
        self.current_player.add_coins(1)
        
        _, new_pos = self.board.move_camel(color, spaces)
        
        self.event_queue.append({
            "type": "roll",
            "player": self.current_player.name,
            "camel": color,
            "spaces": spaces,
            "new_pos": new_pos
        })
        
        # Save round to db
        # Note: avoiding circular import by just keeping a generic dict for round record
        from database.models import RoundRecord
        rr = RoundRecord(
            id=None,
            game_id=self.game_id,
            round_number=self.round_number,
            camel_moved=color,
            spaces_moved=spaces,
            leg_ended=self.pyramid.is_empty()
        )
        self.db.save_round(rr)
        
        owner = self._get_tile_owner(new_pos)
        if owner and owner != self.current_player:
            owner.add_coins(1)
            self.event_queue.append({
                "type": "tile_hit",
                "owner": owner.name,
                "amount": 1
            })

        winner = self.board.get_race_winner()
        leg_ended = self.pyramid.is_empty()

        if winner:
            self.is_race_over = True
            
        if leg_ended and not self.is_race_over:
            self.resolve_leg_internal()
            self.pyramid.reset_leg()
            
            self.board.desert_tiles.clear()
            for p in self.players:
                p.has_placed_tile = False
                p.tile_space = -1
                
        self.round_number += 1
        self.advance_turn()
        return (color, spaces)

    def _get_tile_owner(self, space: int) -> Optional[Player]:
        for p in self.players:
            if p.has_placed_tile and p.tile_space == space:
                return p
        return None

    def do_leg_bet(self, camel_color: str) -> Optional[int]:
        if not self.bet_manager: return None
        val = self.bet_manager.place_leg_bet(self.current_player.name, camel_color)
        if val is not None:
            self.event_queue.append({
                "type": "leg_bet",
                "player": self.current_player.name,
                "camel": camel_color,
                "value": val
            })
            from database.models import BetRecord
            br = BetRecord(
                id=None,
                game_id=self.game_id,
                player_id=0, # handled by db_manager
                round_id=None,
                bet_type='leg',
                camel_color=camel_color,
                coins_won=0 # Updated later or not strictly needed
            )
            self.db.save_bet(self.game_id, self.current_player.name, br)
            self.advance_turn()
        return val

    def do_race_bet(self, camel_color: str, bet_type: str) -> bool:
        if not self.bet_manager: return False
        success = self.bet_manager.place_race_bet(self.current_player.name, camel_color, bet_type)
        if success:
            self.event_queue.append({
                "type": "race_bet",
                "player": self.current_player.name,
                "camel": camel_color,
                "bet_type": bet_type
            })
            db_bet_type = 'race_winner' if bet_type == 'winner' else 'race_loser'
            from database.models import BetRecord
            br = BetRecord(
                id=None,
                game_id=self.game_id,
                player_id=0,
                round_id=None,
                bet_type=db_bet_type,
                camel_color=camel_color,
                coins_won=0
            )
            self.db.save_bet(self.game_id, self.current_player.name, br)
            self.advance_turn()
        return success

    def do_place_tile(self, space: int, tile_type: str) -> bool:
        val = 1 if tile_type == "plus" else -1
        p = self.current_player
        
        if p.has_placed_tile and p.tile_space in self.board.desert_tiles:
            del self.board.desert_tiles[p.tile_space]
            
        success = self.board.place_tile(space, val)
        if success:
            p.has_placed_tile = True
            p.tile_value = val
            p.tile_space = space
            self.event_queue.append({
                "type": "place_tile",
                "player": p.name,
                "space": space,
                "tile_type": tile_type
            })
            self.advance_turn()
            return True
            
        if p.has_placed_tile and p.tile_space != -1:
             self.board.place_tile(p.tile_space, p.tile_value)
        return False

    def resolve_leg_internal(self):
        standings = self.get_standings()
        if len(standings) < 2: return
        first = standings[0][0]
        second = standings[1][0]
        
        if not self.bet_manager: return
        payouts = self.bet_manager.resolve_leg(first, second)
        for p in self.players:
            if p.name in payouts:
                p.add_coins(payouts[p.name])
                
        self.event_queue.append({
            "type": "leg_resolved",
            "first": first,
            "second": second,
            "payouts": payouts
        })
        self.bet_manager.reset_leg_bets()

    def resolve_race(self) -> Dict[str, int]:
        standings = self.get_standings()
        if not standings: return {}
        first = standings[0][0]
        last = standings[-1][0]
        
        if not self.bet_manager: return {}
        payouts = self.bet_manager.resolve_race(first, last)
        
        # Calculate final ranks
        self.players.sort(key=lambda p: p.coins, reverse=True)
        player_results = []
        for rank, p in enumerate(self.players, 1):
            if p.name in payouts:
                p.add_coins(payouts[p.name])
            player_results.append({
                "name": p.name,
                "coins": p.coins,
                "rank": rank
            })
                
        self.event_queue.append({
            "type": "race_resolved",
            "first": first,
            "last": last,
            "payouts": payouts
        })
        
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.update_game_end(
            self.game_id, 
            now, 
            self.players[0].name, 
            self.round_number, 
            player_results
        )
        return payouts

    def get_standings(self) -> List[Tuple[str, int, int]]:
        return self.board.get_standings()

    def advance_turn(self):
        if not self.is_race_over:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
