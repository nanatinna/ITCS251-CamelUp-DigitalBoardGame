"""
board.py - Board class holding the track and camels.
"""
from typing import List, Optional, Tuple, Dict
from config.settings import TRACK_LENGTH, CAMEL_COLORS
from .camel import Camel

class Board:
    def __init__(self):
        self.track: List[List[Camel]] = [[] for _ in range(TRACK_LENGTH + 1)]
        self.camels: Dict[str, Camel] = {}
        self.desert_tiles: Dict[int, int] = {}

    def setup_camels(self, initial_positions: Dict[str, int]):
        """Places camels on starting positions based on initial rolls."""
        self.track = [[] for _ in range(TRACK_LENGTH + 1)]
        self.camels.clear()
        
        for color in CAMEL_COLORS:
            pos = initial_positions.get(color, 1)
            camel = Camel(color=color, position=pos)
            self.camels[color] = camel
            
            camel.stack_order = len(self.track[pos])
            self.track[pos].append(camel)

    def move_camel(self, camel_color: str, spaces: int) -> Tuple[str, int]:
        """Moves a camel and any camels stacked on top."""
        if camel_color not in self.camels:
            return camel_color, 0
            
        target_camel = self.camels[camel_color]
        old_pos = target_camel.position
        
        if old_pos >= TRACK_LENGTH:
            return camel_color, old_pos

        stack_idx = target_camel.stack_order
        moving_stack = self.track[old_pos][stack_idx:]
        self.track[old_pos] = self.track[old_pos][:stack_idx]
        
        new_pos = old_pos + spaces
        if new_pos > TRACK_LENGTH:
            new_pos = TRACK_LENGTH
            
        modifier = self.desert_tiles.get(new_pos, 0)
        
        if modifier == 1:
            new_pos += 1
            if new_pos > TRACK_LENGTH:
                new_pos = TRACK_LENGTH
            for c in moving_stack:
                c.position = new_pos
                c.stack_order = len(self.track[new_pos])
                self.track[new_pos].append(c)
                
        elif modifier == -1:
            new_pos -= 1
            if new_pos < 1:
                new_pos = 1
            for c in moving_stack:
                c.position = new_pos
            for i, c in enumerate(moving_stack):
                c.stack_order = i
            existing_stack = self.track[new_pos]
            for i, c in enumerate(existing_stack):
                c.stack_order = i + len(moving_stack)
            self.track[new_pos] = moving_stack + existing_stack
        else:
            for c in moving_stack:
                c.position = new_pos
                c.stack_order = len(self.track[new_pos])
                self.track[new_pos].append(c)

        return camel_color, new_pos

    def place_tile(self, space: int, value: int) -> bool:
        """Places a desert tile if valid."""
        if space < 2 or space >= TRACK_LENGTH:
            return False
            
        for adj in (space - 1, space, space + 1):
            if adj in self.desert_tiles:
                return False
                
        if len(self.track[space]) > 0:
            return False

        self.desert_tiles[space] = value
        return True

    def get_leader(self) -> Optional[Camel]:
        """Returns the camel currently in 1st place."""
        standings = self.get_standings()
        if standings:
            color = standings[0][0]
            return self.camels[color]
        return None

    def get_race_winner(self) -> Optional[Camel]:
        """If any camel is at TRACK_LENGTH, return the winner."""
        if len(self.track[TRACK_LENGTH]) > 0:
            return self.track[TRACK_LENGTH][-1]
        return None

    def get_standings(self) -> List[Tuple[str, int, int]]:
        """Returns ordered standings from 1st to last place."""
        standings = []
        for space in range(TRACK_LENGTH, 0, -1):
            stack = self.track[space]
            for camel in reversed(stack):
                standings.append((camel.color, camel.position, camel.stack_order))
        return standings
