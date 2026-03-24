"""
base_screen.py - Abstract Screen base class
"""
import pygame
from typing import Callable

class BaseScreen:
    def __init__(self, screen: pygame.Surface, switch_screen: Callable):
        self.screen = screen
        self.switch_screen = switch_screen
        self.bg_image = None
        import os
        if os.path.exists("assets/background.png"):
            try:
                img = pygame.image.load("assets/background.png").convert()
                self.bg_image = pygame.transform.scale(img, (screen.get_width(), screen.get_height()))
            except: pass

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        pass

    def draw_bg(self):
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            from config.settings import COLORS
            self.screen.fill(COLORS['BACKGROUND'])

    def draw(self):
        pass
