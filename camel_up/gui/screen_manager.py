"""
screen_manager.py - Manages screen switching and app loop
"""
import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from gui.screens.menu_screen import MenuScreen
from gui.screens.setup_screen import SetupScreen
from gui.screens.game_screen import GameScreen
from gui.screens.leg_result_screen import LegResultScreen
from gui.screens.game_over_screen import GameOverScreen
from gui.screens.history_screen import HistoryScreen
from gui.screens.how_to_play_screen import HowToPlayScreen
from database.db_manager import DBManager

class ScreenManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Camel Up!")
        self.clock = pygame.time.Clock()
        self.db_manager = DBManager()
        self.running = True
        
        self.screens = {
            "menu": MenuScreen,
            "setup": SetupScreen,
            "game": GameScreen,
            "leg_result": LegResultScreen,
            "game_over": GameOverScreen,
            "history": HistoryScreen,
            "how_to_play": HowToPlayScreen
        }
        self.current_screen = None
        self.switch_screen("menu")

    def switch_screen(self, screen_name: str, **kwargs):
        if screen_name in self.screens:
            self.current_screen = self.screens[screen_name](
                screen=self.screen, 
                switch_screen=self.switch_screen,
                db_manager=self.db_manager,
                **kwargs
            )

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.current_screen.handle_event(event)

            self.current_screen.update(dt)
            self.current_screen.draw()
            pygame.display.flip()
            
        pygame.quit()
