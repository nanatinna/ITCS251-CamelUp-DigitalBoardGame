"""
how_to_play_screen.py - Game rules
"""
import pygame
from .base_screen import BaseScreen
from gui.components.ui_elements import Button, Label, Panel
from config.settings import COLORS

class HowToPlayScreen(BaseScreen):
    def __init__(self, screen, switch_screen, db_manager, **kwargs):
        super().__init__(screen, switch_screen)
        
        self.title = Label(50, 30, "How to Play Camel Up", size=48)
        self.btn_back = Button(50, 680, 200, 50, "Back to Menu", self.on_back)
        
        self.panel = Panel(50, 100, 924, 550)
        
        self.rules = [
            "Welcome to Camel Up!",
            "",
            "1. THE RACE:",
            "  Camels race around the track. If a camel lands on another, they stack!",
            "  The camel on top is considered ahead. A camel carrying others moves them all.",
            "",
            "2. YOUR TURN ACTIONS (Take 1 per turn):",
            "  - Roll the Pyramid: Moves a random camel 1-3 spaces. You get 1 coin.",
            "  - Bet on a Leg: Take a betting tile for the camel you think will win this leg.",
            "  - Place Desert Tile: Place a +/- 1 tile to help or hinder camels.",
            "  - Bet on Overall Race: Secretly bet on the overall Winner or Loser.",
            "",
            "3. SCORING:",
            "  A Leg ends when 5 dice are rolled. The game ends when a camel crosses the finish line.",
            "  Points are awarded for correct bets and penalized for wrong ones.",
            "",
            "May the best camel win!"
        ]
        
    def on_back(self):
        self.switch_screen("menu")

    def handle_event(self, event):
        self.btn_back.update(event)

    def draw(self):
        self.draw_bg()
        self.panel.draw(self.screen)
        self.title.draw(self.screen)
        
        from gui.components.ui_elements import get_font
        font = get_font(24)
        
        y = 120
        for line in self.rules:
            img = font.render(line, True, COLORS['TEXT'])
            self.screen.blit(img, (70, y))
            y += 28
            
        self.btn_back.draw(self.screen)
