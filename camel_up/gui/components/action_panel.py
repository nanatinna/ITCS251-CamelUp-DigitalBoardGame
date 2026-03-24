"""
action_panel.py - Action panel containing buttons
"""
import pygame
from typing import List
from .ui_elements import Button

class ActionPanel:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.rect = pygame.Rect(x, y, w, h)
        self.actions: dict[str, Button] = {}
        self._build_buttons()

    def _build_buttons(self):
        btn_x = self.rect.x + 10
        btn_w = self.rect.width - 20
        btn_h = 40
        
        self.actions["roll"] = Button(btn_x, self.rect.y + 10, btn_w, btn_h, "Roll Pyramid", None)
        self.actions["leg_bet"] = Button(btn_x, self.rect.y + 60, btn_w, btn_h, "Take Leg Bet", None)
        self.actions["race_bet"] = Button(btn_x, self.rect.y + 110, btn_w, btn_h, "Take Race Bet", None)
        self.actions["place_tile"] = Button(btn_x, self.rect.y + 160, btn_w, btn_h, "Place Desert Tile", None)

    def set_callbacks(self, on_roll, on_leg_bet, on_race_bet, on_place_tile):
        self.actions["roll"].on_click = on_roll
        self.actions["leg_bet"].on_click = on_leg_bet
        self.actions["race_bet"].on_click = on_race_bet
        self.actions["place_tile"].on_click = on_place_tile

    def update_state(self, available_actions: List[str]):
        for name, btn in self.actions.items():
            btn.disabled = name not in available_actions

    def update(self, event: pygame.event.Event):
        for btn in self.actions.values():
            btn.update(event)

    def draw(self, surface: pygame.Surface):
        from .ui_elements import Panel
        Panel(self.rect.x, self.rect.y, self.rect.width, self.rect.height).draw(surface)
        for btn in self.actions.values():
            btn.draw(surface)
