"""
history_screen.py - Game history + stats from DB
"""
import pygame
from .base_screen import BaseScreen
from gui.components.ui_elements import Button, Label, TextInput, get_font
from config.settings import COLORS

class HistoryScreen(BaseScreen):
    def __init__(self, screen, switch_screen, db_manager, **kwargs):
        super().__init__(screen, switch_screen)
        self.db = db_manager
        
        cx = screen.get_width() // 2
        self.title = Label(cx - 100, 30, "Game History", size=36)
        
        self.btn_back = Button(20, 20, 100, 40, "Back", self.on_back)
        
        self.history = self.db.get_history(limit=10)
        
        self.search_lbl = Label(20, 400, "Search Player Stats:", size=24)
        self.search_inp = TextInput(250, 395, 200, 40)
        self.btn_search = Button(470, 395, 100, 40, "Search", self.on_search)
        
        self.stats_result = None

    def on_back(self):
        self.switch_screen("menu")
        
    def on_search(self):
        name = self.search_inp.text.strip()
        if name:
            self.stats_result = self.db.get_player_stats(name)
            if not self.stats_result:
                self.stats_result = "Not Found"

    def handle_event(self, event):
        self.btn_back.update(event)
        self.search_inp.update(event)
        self.btn_search.update(event)

    def draw(self):
        self.screen.fill(COLORS['BACKGROUND'])
        self.title.draw(self.screen)
        self.btn_back.draw(self.screen)
        
        font = get_font(20)
        
        y = 100
        header = font.render("ID | Date | Winner | Rounds | Players", True, COLORS['TEXT'])
        self.screen.blit(header, (50, y))
        y += 30
        
        for g in self.history:
            dt = g.get('ended_at', 'N/A')
            if dt and hasattr(dt, 'strftime'):
                dt = dt.strftime("%Y-%m-%d")
            txt = f"#{g.get('id')} | {dt} | {g.get('winner_name')} | {g.get('total_rounds')} | {g.get('player_count')}"
            img = font.render(txt, True, COLORS['TEXT'])
            self.screen.blit(img, (50, y))
            y += 25
            
        self.search_lbl.draw(self.screen)
        self.search_inp.draw(self.screen)
        self.btn_search.draw(self.screen)
        
        if self.stats_result:
            if isinstance(self.stats_result, str):
                msg = Label(20, 450, "Player not found.", color=COLORS['ERROR'])
                msg.draw(self.screen)
            else:
                s = self.stats_result
                txt1 = f"Name: {s.name} | Played: {s.games_played} | Won: {s.games_won}"
                txt2 = f"Total Coins: {s.total_coins_earned} | Best: {s.best_score}"
                Label(20, 450, txt1, size=20).draw(self.screen)
                Label(20, 480, txt2, size=20).draw(self.screen)
