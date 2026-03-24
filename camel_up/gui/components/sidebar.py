"""
sidebar.py - Renders player hand info and active leg bet tiles
"""
import pygame
from config.settings import COLORS, CAMEL_COLORS
from .ui_elements import Panel
from game_logic.game_engine import GameEngine

class Sidebar:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.rect = pygame.Rect(x, y, w, h)
        self.panel = Panel(x, y, w, h)
        self.font = pygame.font.SysFont(None, 24)
        
    def draw(self, surface: pygame.Surface, engine: GameEngine):
        self.panel.draw(surface)
        if getattr(engine, 'current_player_idx', None) is None or not engine.players:
            return
            
        p = engine.current_player
        y_offset = self.rect.y + 15
        x_offset = self.rect.x + 15
        
        lbl_p = self.font.render(f"Current Player: {p.name}", True, COLORS['TEXT'])
        surface.blit(lbl_p, (x_offset, y_offset))
        y_offset += 30
        
        lbl_c = self.font.render(f"Coins: {p.coins}", True, COLORS['TEXT'])
        surface.blit(lbl_c, (x_offset, y_offset))
        y_offset += 40
        
        remaining = len(engine.pyramid.remaining_dice)
        lbl_pyr = self.font.render(f"Pyramid Dice: {remaining}", True, COLORS['TEXT'])
        surface.blit(lbl_pyr, (x_offset, y_offset))
        y_offset += 40
        
        lbl_tiles = self.font.render("Leg Bet Tiles:", True, COLORS['TEXT'])
        surface.blit(lbl_tiles, (x_offset, y_offset))
        y_offset += 25
        
        if engine.bet_manager:
            for color in CAMEL_COLORS:
                tiles = engine.bet_manager.leg_tiles[color]
                top_val = tiles[0] if tiles else "Empty"
                count = len(tiles)
                
                real_color = getattr(COLORS, f'CAMEL_{color.upper()}', COLORS['TEXT'])
                
                txt = f"{color}: {top_val} ({count} left)"
                img = self.font.render(txt, True, COLORS['TEXT'])
                surface.blit(img, (x_offset + 10, y_offset))
                
                box_rect = pygame.Rect(x_offset - 5, y_offset + 2, 10, 10)
                if color == "White": real_color = (200, 200, 200)
                pygame.draw.rect(surface, real_color, box_rect)
                pygame.draw.rect(surface, COLORS['BLACK'], box_rect, 1)

                y_offset += 25
