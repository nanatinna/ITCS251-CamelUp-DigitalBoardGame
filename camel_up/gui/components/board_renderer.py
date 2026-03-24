"""
board_renderer.py - Draw the 16-space track
"""
import pygame
import math
from config.settings import COLORS, TRACK_LENGTH

class BoardRenderer:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.font = pygame.font.SysFont(None, 24)
        self.space_centers = {}
        
        cx, cy = self.rect.center
        r_x = self.rect.width / 2 - 60
        r_y = self.rect.height / 2 - 60
        
        self.space_centers[0] = (cx, self.rect.bottom - 40)
        
        for i in range(1, TRACK_LENGTH + 1):
            angle = math.pi / 2 + (i / TRACK_LENGTH) * 2 * math.pi
            x = cx + r_x * math.cos(angle)
            y = cy + r_y * math.sin(angle)
            self.space_centers[i] = (int(x), int(y))

    def get_space_center(self, space: int) -> tuple[int, int]:
        if space > TRACK_LENGTH:
            space = TRACK_LENGTH
        return self.space_centers.get(space, (0,0))

    def draw(self, surface: pygame.Surface, desert_tiles: dict[int, int]):
        for i in range(TRACK_LENGTH + 1):
            x, y = self.space_centers[i]
            rect = pygame.Rect(0, 0, 50, 50)
            rect.center = (x, y)
            
            bg_color = COLORS['WHITE']
            if i in desert_tiles:
                val = desert_tiles[i]
                if val == 1:
                    bg_color = COLORS['DESERT_PLUS']
                else:
                    bg_color = COLORS['DESERT_MINUS']
            elif i == 0:
                bg_color = (200, 200, 200)
                
            pygame.draw.rect(surface, bg_color, rect, border_radius=5)
            pygame.draw.rect(surface, COLORS['BLACK'], rect, 2, border_radius=5)
            
            text = str(i) if i > 0 else "Start"
            img = self.font.render(text, True, COLORS['TEXT'])
            text_rect = img.get_rect(center=(x, y - 15))
            surface.blit(img, text_rect)
