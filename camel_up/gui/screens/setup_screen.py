"""
setup_screen.py - Player name entry
"""
import pygame
from .base_screen import BaseScreen
from gui.components.ui_elements import Button, Label, TextInput
from config.settings import COLORS, MAX_PLAYERS, MIN_PLAYERS

class SetupScreen(BaseScreen):
    def __init__(self, screen, switch_screen, db_manager, **kwargs):
        super().__init__(screen, switch_screen)
        self.db = db_manager
        
        cx = screen.get_width() // 2
        
        self.title = Label(cx - 120, 50, "Game Setup", size=36)
        
        self.player_inputs = []
        start_y = 150
        for i in range(MAX_PLAYERS):
            lbl = Label(cx - 150, start_y + i*60 + 10, f"Player {i+1}:", size=24)
            inp = TextInput(cx - 50, start_y + i*60, 200, 40)
            if i < MIN_PLAYERS:
                inp.text = f"Player {i+1}"
            self.player_inputs.append((lbl, inp))
            
        self.btn_start = Button(cx - 100, 500, 200, 50, "Start Game", self.on_start)
        self.btn_back = Button(cx - 100, 570, 200, 50, "Back", self.on_back)
        self.error_msg = ""
        
    def on_start(self):
        names = [inp.text.strip() for _, inp in self.player_inputs if inp.text.strip()]
        if len(names) < MIN_PLAYERS:
            self.error_msg = f"Need at least {MIN_PLAYERS} players!"
            return
        if len(set(names)) != len(names):
            self.error_msg = "Names must be unique!"
            return
            
        self.switch_screen("game", player_names=names)

    def on_back(self):
        self.switch_screen("menu")

    def handle_event(self, event):
        for _, inp in self.player_inputs:
            inp.update(event)
        self.btn_start.update(event)
        self.btn_back.update(event)

    def draw(self):
        self.draw_bg()
        self.title.draw(self.screen)
        
        for lbl, inp in self.player_inputs:
            lbl.draw(self.screen)
            inp.draw(self.screen)
            
        if self.error_msg:
            err = Label(self.screen.get_width()//2 - 100, 450, self.error_msg, color=COLORS['ERROR'])
            err.draw(self.screen)
            
        self.btn_start.draw(self.screen)
        self.btn_back.draw(self.screen)
