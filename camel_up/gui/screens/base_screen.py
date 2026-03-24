"""
base_screen.py - Abstract Screen base class
"""
import pygame
from typing import Callable

class BaseScreen:
    def __init__(self, screen: pygame.Surface, switch_screen: Callable):
        self.screen = screen
        self.switch_screen = switch_screen

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        pass

    def draw(self):
        pass
