"""
game_over_screen.py - Winner announcement
"""
import pygame
from .base_screen import BaseScreen
from gui.components.ui_elements import Button, Label
from config.settings import COLORS

class GameOverScreen(BaseScreen):
    def __init__(self, screen, switch_screen, db_manager, **kwargs):
        super().__init__(screen, switch_screen)
        self.db = db_manager
        
        self.players = kwargs.get("players", []) 
        
        cx = screen.get_width() // 2
        cy = screen.get_height() // 2
        
        winner_name = self.players[0].name if self.players else "Unknown"
        self.title = Label(cx - 150, 50, f"Winner: {winner_name}!", size=48, color=(200, 50, 50))
        
        self.btn_replay = Button(cx - 100, cy + 150, 200, 50, "Play Again", self.on_replay)
        self.btn_menu = Button(cx - 100, cy + 220, 200, 50, "Main Menu", self.on_menu)

    def on_replay(self):
        self.switch_screen("setup")
        
    def on_menu(self):
        self.switch_screen("menu")

    def handle_event(self, event):
        self.btn_replay.update(event)
        self.btn_menu.update(event)

    def draw(self):
        self.screen.fill(COLORS['BACKGROUND'])
        self.title.draw(self.screen)
        
        from gui.components.ui_elements import get_font
        font = get_font(30)
        
        cx = self.screen.get_width() // 2
        y = 150
        for i, p in enumerate(self.players):
            txt = f"{i+1}. {p.name} - {p.coins} coins"
            img = font.render(txt, True, COLORS['TEXT'])
            rect = img.get_rect(center=(cx, y))
            self.screen.blit(img, rect)
            y += 40
            
        self.btn_replay.draw(self.screen)
        self.btn_menu.draw(self.screen)
