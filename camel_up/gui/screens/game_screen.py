"""
game_screen.py - Main game board view
"""
import pygame
from .base_screen import BaseScreen
from gui.components.board_renderer import BoardRenderer
from gui.components.camel_renderer import CamelRenderer
from gui.components.sidebar import Sidebar
from gui.components.action_panel import ActionPanel
from gui.components.ui_elements import Label, Button, get_font
from game_logic.game_engine import GameEngine
from config.settings import BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT, SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, SIDEBAR_HEIGHT, COLORS, CAMEL_COLORS
from typing import List, Dict

class Animation:
    def __init__(self, duration, callback=None):
        self.timer = 0.0
        self.duration = duration
        self.callback = callback
        self.done = False
        
    def update(self, dt):
        if self.done: return
        self.timer += dt
        if self.timer >= self.duration:
            self.done = True
            if self.callback:
                self.callback()

class GameScreen(BaseScreen):
    def __init__(self, screen, switch_screen, db_manager, **kwargs):
        super().__init__(screen, switch_screen)
        
        if "existing_engine" in kwargs:
            self.engine = kwargs["existing_engine"]
        else:
            self.engine = GameEngine(db_manager)
            player_names = kwargs.get("player_names", ["Player 1", "Player 2"])
            self.engine.start_game(player_names)
        
        board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
        self.board_renderer = BoardRenderer(board_rect)
        self.camel_renderer = CamelRenderer()
        
        self.sidebar = Sidebar(SIDEBAR_X, BOARD_Y, SIDEBAR_WIDTH, SIDEBAR_HEIGHT - 250)
        self.action_panel = ActionPanel(SIDEBAR_X, SIDEBAR_Y + SIDEBAR_HEIGHT - 230, SIDEBAR_WIDTH, 230)
        
        self.action_panel.set_callbacks(
            on_roll=self.on_roll,
            on_leg_bet=self.on_leg_bet_click,
            on_race_bet=self.on_race_bet_click,
            on_place_tile=self.on_place_tile_click
        )
        
        self.error_msg = ""
        self.error_timer = 0.0
        
        self.animations = []
        self.floating_texts = [] 
        self.animating_camels = False
        self.standings = self.engine.get_standings()
        
        self.show_bet_modal = False
        self.bet_modal_type = ""
        self.bet_buttons = []
        
        self.show_tile_modal = False
        self.tile_buttons = []
        
    def show_error(self, msg: str):
        self.error_msg = msg
        self.error_timer = 3.0

    def on_roll(self):
        if self.animating_camels: return
        res = self.engine.do_roll()
        if res:
            self._process_events()

    def on_leg_bet_click(self):
        if self.animating_camels: return
        self.show_bet_modal = True
        self.bet_modal_type = "leg"
        self._build_color_modal(self._handle_leg_bet_choice)

    def on_race_bet_click(self):
        if self.animating_camels: return
        self.show_bet_modal = True
        self.bet_modal_type = "race"
        self._build_race_modal()
        
    def on_place_tile_click(self):
        if self.animating_camels: return
        self.show_tile_modal = True
        self._build_tile_modal()

    def _build_color_modal(self, callback):
        self.bet_buttons = []
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2 - 100
        for i, color in enumerate(CAMEL_COLORS):
            if self.bet_modal_type == "leg":
                tiles = self.engine.bet_manager.leg_tiles[color]
                if not tiles:
                    continue
            btn = Button(cx - 100, cy + i*50, 200, 40, color, lambda c=color: callback(c))
            self.bet_buttons.append(btn)
        self.bet_buttons.append(Button(cx - 100, cy + 300, 200, 40, "Cancel", self._close_modal))

    def _build_race_modal(self):
        self.bet_buttons = []
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2 - 150
        
        def pick_winner(color):
            success = self.engine.do_race_bet(color, "winner")
            if not success: self.show_error("Already bet on Winner!")
            self._close_modal()
            self._process_events()
            
        def pick_loser(color):
            success = self.engine.do_race_bet(color, "loser")
            if not success: self.show_error("Already bet on Loser!")
            self._close_modal()
            self._process_events()

        for i, color in enumerate(CAMEL_COLORS):
            b1 = Button(cx - 210, cy + i*50, 200, 40, f"Winner: {color}", lambda c=color: pick_winner(c))
            b2 = Button(cx + 10, cy + i*50, 200, 40, f"Loser: {color}", lambda c=color: pick_loser(c))
            self.bet_buttons.extend([b1, b2])
            
        self.bet_buttons.append(Button(cx - 100, cy + 350, 200, 40, "Cancel", self._close_modal))

    def _build_tile_modal(self):
        self.tile_buttons = []
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2 - 200
        
        grid_x = cx - 250
        grid_y = cy
        
        def place_tile(sp, val):
            success = self.engine.do_place_tile(sp, val)
            if not success:
                self.show_error("Invalid placement — space occupied or adjacent")
            self._close_modal()
            self._process_events()
            
        for i, sp in enumerate(range(2, 16)):
            x = grid_x + (i % 7) * 70
            y = grid_y + (i // 7) * 90
            
            b1 = Button(x, y, 60, 30, f"{sp} (+)", lambda s=sp: place_tile(s, "plus"))
            b2 = Button(x, y+35, 60, 30, f"{sp} (-)", lambda s=sp: place_tile(s, "minus"))
            self.tile_buttons.extend([b1, b2])
            
        self.tile_buttons.append(Button(cx - 100, cy + 250, 200, 40, "Cancel", self._close_modal))

    def _close_modal(self):
        self.show_bet_modal = False
        self.show_tile_modal = False
        self.bet_buttons = []
        self.tile_buttons = []

    def _handle_leg_bet_choice(self, color):
        val = self.engine.do_leg_bet(color)
        if val is None:
            self.show_error(f"No more tiles for {color}")
        self._close_modal()
        self._process_events()

    def _process_events(self):
        for evt in self.engine.event_queue:
            if evt["type"] == "roll":
                self._add_floating_text("+1", SIDEBAR_X + 100, 150, COLORS['TEXT'])
                self.animating_camels = True
                def on_anim_done():
                    self.animating_camels = False
                    self.standings = self.engine.get_standings()
                    self._check_delayed_resolves()
                self.animations.append(Animation(0.3, on_anim_done))
            elif evt["type"] == "tile_hit":
                self._add_floating_text("+1 (Tile Hit)", SIDEBAR_X + 100, 150, COLORS['TEXT'])
                
        if not self.animating_camels:
            self.standings = self.engine.get_standings()
            self._check_delayed_resolves()

    def _check_delayed_resolves(self):
        for evt in self.engine.event_queue:
            if evt["type"] == "race_resolved":
                self.switch_screen("game_over", players=self.engine.players)
                return
            elif evt["type"] == "leg_resolved":
                self.switch_screen("leg_result", 
                                   first=evt["first"], 
                                   second=evt["second"], 
                                   payouts=evt["payouts"],
                                   game_engine=self.engine)
                return
        self.engine.event_queue.clear()

    def _add_floating_text(self, text, x, y, color):
        self.floating_texts.append([text, (x, y), color, 1.5]) 
        
    def handle_event(self, event):
        if self.show_bet_modal:
            for b in self.bet_buttons: b.update(event)
            return
        if self.show_tile_modal:
            for b in self.tile_buttons: b.update(event)
            return
            
        if not self.animating_camels:
            self.action_panel.update(event)

    def update(self, dt):
        if self.error_timer > 0:
            self.error_timer -= dt
            
        for a in self.animations:
            a.update(dt)
        self.animations = [a for a in self.animations if not a.done]
        
        for ft in self.floating_texts:
            ft[3] -= dt
            x, y = ft[1]
            ft[1] = (x, y - 20 * dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft[3] > 0]
        
        if not self.animating_camels:
            self.action_panel.update_state(self.engine.available_actions())

    def draw(self):
        self.screen.fill(COLORS['BACKGROUND'])
        
        self.board_renderer.draw(self.screen, self.engine.board.desert_tiles)
        self.camel_renderer.draw(self.screen, self.board_renderer, self.standings)
        
        self.sidebar.draw(self.screen, self.engine)
        self.action_panel.draw(self.screen)
        
        fnt = get_font(24)
        for txt, (x, y), clr, _ in self.floating_texts:
            img = fnt.render(txt, True, clr)
            self.screen.blit(img, (int(x), int(y)))
            
        if self.error_timer > 0:
            rect = pygame.Rect(0, 0, self.screen.get_width(), 40)
            pygame.draw.rect(self.screen, COLORS['ERROR'], rect)
            lbl = get_font(24).render(self.error_msg, True, COLORS['WHITE'])
            self.screen.blit(lbl, (self.screen.get_width()//2 - lbl.get_width()//2, 10))
            
        if self.show_bet_modal or self.show_tile_modal:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0,0))
            for b in self.bet_buttons: b.draw(self.screen)
            for b in self.tile_buttons: b.draw(self.screen)
