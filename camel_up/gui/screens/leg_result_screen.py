"""
leg_result_screen.py - Show leg results
"""
import pygame
from .base_screen import BaseScreen
from gui.components.ui_elements import Button, Label
from config.settings import COLORS

class LegResultScreen(BaseScreen):
    def __init__(self, screen, switch_screen, db_manager, **kwargs):
        super().__init__(screen, switch_screen)
        self.first = kwargs.get("first", "")
        self.second = kwargs.get("second", "")
        self.payouts = kwargs.get("payouts", {})
        self.engine = kwargs.get("game_engine", None)
        
        cx = screen.get_width() // 2
        cy = screen.get_height() // 2
        
        self.title = Label(cx - 150, 50, "Leg Finished!", size=48)
        self.sub = Label(cx - 200, 120, f"1st: {self.first} | 2nd: {self.second}", size=36)
        
        self.btn_cont = Button(cx - 100, cy + 200, 200, 50, "Continue", self.on_continue)

    def on_continue(self):
        self.switch_screen("game", existing_engine=self.engine)

    def handle_event(self, event):
        self.btn_cont.update(event)

    def draw(self):
        self.screen.fill(COLORS['BACKGROUND'])
        self.title.draw(self.screen)
        self.sub.draw(self.screen)
        
        from gui.components.ui_elements import get_font
        font = get_font(28)
        
        cx = self.screen.get_width() // 2
        y = 200
        for name, delta in self.payouts.items():
            sign = "+" if delta >= 0 else ""
            color = COLORS['DESERT_PLUS'] if delta >= 0 else COLORS['DESERT_MINUS']
            if delta < 0: color = COLORS['ERROR']
            txt = f"{name}: {sign}{delta} coins"
            img = font.render(txt, True, color)
            self.screen.blit(img, (cx - 100, y))
            y += 40
            
        self.btn_cont.draw(self.screen)
