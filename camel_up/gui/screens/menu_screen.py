"""
menu_screen.py - Main menu
"""
import pygame
from .base_screen import BaseScreen
from gui.components.ui_elements import Button, Label
from config.settings import COLORS

class MenuScreen(BaseScreen):
    def __init__(self, screen, switch_screen, db_manager, **kwargs):
        super().__init__(screen, switch_screen)
        
        cx = screen.get_width() // 2
        cy = screen.get_height() // 2
        
        self.title = Label(cx - 100, cy - 150, "Camel Up!", size=48)
        
        self.btn_new = Button(cx - 100, cy - 80, 200, 50, "New Game", self.on_new)
        self.btn_hist = Button(cx - 100, cy - 10, 200, 50, "History", self.on_hist)
        self.btn_how = Button(cx - 100, cy + 60, 200, 50, "How to Play", self.on_how)
        self.btn_quit = Button(cx - 100, cy + 130, 200, 50, "Quit", self.on_quit)

    def on_new(self):
        self.switch_screen("setup")
        
    def on_hist(self):
        self.switch_screen("history")
        
    def on_how(self):
        self.switch_screen("how_to_play")
        
    def on_quit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_event(self, event):
        self.btn_new.update(event)
        self.btn_hist.update(event)
        self.btn_how.update(event)
        self.btn_quit.update(event)

    def draw(self):
        self.screen.fill(COLORS['BACKGROUND'])
        self.title.draw(self.screen)
        self.btn_new.draw(self.screen)
        self.btn_hist.draw(self.screen)
        self.btn_how.draw(self.screen)
        self.btn_quit.draw(self.screen)
