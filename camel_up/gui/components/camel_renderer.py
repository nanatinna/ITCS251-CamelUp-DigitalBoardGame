"""
camel_renderer.py - Draw stacked camels
"""
import pygame
from typing import List, Tuple
from config.settings import COLORS

class CamelRenderer:
    def __init__(self):
        self.camel_w = 40
        self.camel_h = 30
        self.color_map = {
            "White": COLORS["CAMEL_WHITE"],
            "Orange": COLORS["CAMEL_ORANGE"],
            "Green": COLORS["CAMEL_GREEN"],
            "Blue": COLORS["CAMEL_BLUE"],
            "Yellow": COLORS["CAMEL_YELLOW"]
        }
        self.base_img = None
        import os
        if os.path.exists("assets/camel_white.png"):
            try:
                img = pygame.image.load("assets/camel_white.png").convert_alpha()
                self.base_img = pygame.transform.scale(img, (self.camel_w, self.camel_h))
            except: pass

    def draw(self, surface: pygame.Surface, board_renderer, standings: List[Tuple[str, int, int]]):
        pos_map = {}
        for color, pos, order in standings:
            if pos not in pos_map:
                pos_map[pos] = []
            pos_map[pos].append((color, order))
            
        for pos, camels in pos_map.items():
            camels.sort(key=lambda x: x[1])
            
            cx, cy = board_renderer.get_space_center(pos)
            base_y = cy + 15
            
            for i, (color, _) in enumerate(camels):
                rect = pygame.Rect(0, 0, self.camel_w, self.camel_h)
                rect.centerx = cx
                rect.bottom = base_y - i * (self.camel_h - 5)
                
                real_color = self.color_map.get(color, (0,0,0))
                
                if self.base_img:
                    tinted = self.base_img.copy()
                    if color != "White":
                        tinted.fill(real_color, special_flags=pygame.BLEND_RGB_MULT)
                    surface.blit(tinted, rect)
                else:
                    pygame.draw.rect(surface, real_color, rect, border_radius=3)
                    pygame.draw.rect(surface, COLORS['BLACK'], rect, 2, border_radius=3)
