import pygame
import pygame_gui

from gui.theme import (
    SAND_LIGHT, WOOD_DARK, WOOD_MID, TEXT_LIGHT, TEXT_DARK,
    GOLD, PARCHMENT_DARK, WINDOW_W, WINDOW_H,
    generate_background_surface, load_font,
)
from storage.database import get_leaderboard, init_db
from storage.save_manager import has_save


class StartScreen:
    """Title / lobby screen with player-count selector, name inputs, leaderboard."""

    _DEFAULT_NAMES = ['Alice', 'Bob', 'Carol', 'Dave']

    def __init__(self, app):
        self.app = app
        self.ui_manager  = app.ui_manager
        self._background = None
        self._logo       = None
        self._font_title = None
        self._font_sub   = None
        self._font       = None
        self._font_small = None

        self.player_count  = 2
        self.count_buttons: dict = {}
        self.name_entries:  list = []
        self.start_button        = None
        self.load_button         = None
        self.leaderboard_data    = []

        self._setup_ui()

    # ---------------------------------------------------------------- setup
    def _setup_ui(self):
        try:
            init_db()
            self.leaderboard_data = get_leaderboard(10)
        except Exception:
            self.leaderboard_data = []

        cx = WINDOW_W // 2

        # Player-count toggle buttons
        for i, count in enumerate([2, 3, 4]):
            bx = cx - 110 + i * 80
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(bx, 320, 60, 36),
                text=str(count),
                manager=self.ui_manager,
            )
            self.count_buttons[count] = btn

        # Name-entry fields
        for i in range(4):
            entry = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(cx - 120, 380 + i * 50, 240, 36),
                manager=self.ui_manager,
            )
            entry.set_text(self._DEFAULT_NAMES[i])
            self.name_entries.append(entry)

        # Start button
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(cx - 100, 600, 200, 48),
            text='START GAME',
            manager=self.ui_manager,
        )

        # Load button
        if has_save():
            self.load_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(cx - 100, 658, 200, 36),
                text='Load Save',
                manager=self.ui_manager,
            )

        self._refresh_entries()

    def _refresh_entries(self):
        for i, entry in enumerate(self.name_entries):
            if i < self.player_count:
                entry.show()
            else:
                entry.hide()

    # ---------------------------------------------------------------- logo
    def _get_logo(self):
        if self._logo is None:
            try:
                img = pygame.image.load('assets/images/logo.png').convert_alpha()
                w, h = img.get_size()
                max_w, max_h = 520, 210
                scale = min(max_w / w, max_h / h)
                self._logo = pygame.transform.smoothscale(
                    img, (int(w * scale), int(h * scale)))
            except Exception:
                self._logo = False

    # ---------------------------------------------------------------- fonts
    def _get_fonts(self):
        if self._font_title is None:
            self._font_title = load_font(56)
            self._font_sub   = load_font(24)
            self._font       = load_font(16)
            self._font_small = load_font(13)

    # --------------------------------------------------------------- events
    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return

        for count, btn in self.count_buttons.items():
            if event.ui_element == btn:
                self.player_count = count
                self._refresh_entries()
                return

        if event.ui_element == self.start_button:
            self._start_game()
        elif self.load_button and event.ui_element == self.load_button:
            self._kill_ui()
            self.app.load_saved_game()

    def _get_names(self):
        names = []
        for i in range(self.player_count):
            t = self.name_entries[i].get_text().strip()
            names.append(t or f"Player {i + 1}")
        return names

    def _start_game(self):
        names = self._get_names()
        self._kill_ui()
        self.app.start_new_game(names)

    def _kill_ui(self):
        for btn in self.count_buttons.values():
            btn.kill()
        for e in self.name_entries:
            e.kill()
        if self.start_button:
            self.start_button.kill()
        if self.load_button:
            self.load_button.kill()

    # --------------------------------------------------------------- update
    def update(self, time_delta: float):
        pass

    # --------------------------------------------------------------- draw
    def draw(self, surface: pygame.Surface):
        self._get_fonts()
        self._get_logo()

        if self._background is None:
            self._background = generate_background_surface(WINDOW_W, WINDOW_H)
        surface.blit(self._background, (0, 0))

        cx = WINDOW_W // 2

        # Logo / Title
        if self._logo:
            lx = cx - self._logo.get_width() // 2
            surface.blit(self._logo, (lx, 55))
            logo_bottom = 55 + self._logo.get_height()
        else:
            shadow = self._font_title.render("CAMEL UP", True, (40, 20, 5))
            title  = self._font_title.render("CAMEL UP", True, GOLD)
            tx = cx - title.get_width() // 2
            surface.blit(shadow, (tx + 3, 103))
            surface.blit(title,  (tx, 100))
            logo_bottom = 168

        # Sub-title
        sub = self._font_sub.render("The Desert Racing Game", True, TEXT_DARK)
        surface.blit(sub, (cx - sub.get_width() // 2, logo_bottom - 30))

        # Count label
        cl = self._font.render("Number of Players:", True, TEXT_DARK)
        surface.blit(cl, (cx - cl.get_width() // 2, 296))

        # Gold ring around selected count
        for count, btn in self.count_buttons.items():
            if count == self.player_count:
                pygame.draw.rect(surface, GOLD, btn.rect.inflate(6, 6), width=3, border_radius=10)

        # Name field labels
        for i in range(self.player_count):
            lbl = self._font.render(f"Player {i + 1}:", True, TEXT_DARK)
            surface.blit(lbl, (cx - 200, 388 + i * 50))

        # Leaderboard panel (left side)
        ROW_H   = 28
        MAX_ROWS = 8
        lx, lw  = 42, 326
        ly      = 270
        lh      = 58 + MAX_ROWS * ROW_H + 10   # title + header + rows + padding

        lb_bg = pygame.Rect(lx, ly, lw, lh)
        pygame.draw.rect(surface, WOOD_DARK, lb_bg, border_radius=10)
        pygame.draw.rect(surface, WOOD_MID,  lb_bg, width=2, border_radius=10)

        # Title
        lb_title = self._font.render("TOP PLAYERS", True, GOLD)
        surface.blit(lb_title, (lx + lw // 2 - lb_title.get_width() // 2, ly + 10))

        # Title underline
        pygame.draw.line(surface, GOLD,
                         (lx + 14, ly + 30), (lx + lw - 14, ly + 30), 1)

        # Column positions: rank | name | wins | avg
        cx0 = lx + 10   # rank
        cx1 = lx + 38   # name
        cx2 = lx + 210  # wins
        cx3 = lx + 272  # avg

        # Column headers
        hy = ly + 36
        for col_x, hdr in [(cx0, '#'), (cx1, 'Player'), (cx2, 'Wins'), (cx3, 'Avg')]:
            h = self._font_small.render(hdr, True, (200, 175, 110))
            surface.blit(h, (col_x, hy))

        # Header separator
        pygame.draw.line(surface, WOOD_MID,
                         (lx + 14, hy + 18), (lx + lw - 14, hy + 18), 1)

        if self.leaderboard_data:
            rank_colors = [
                (212, 175, 55),   # gold  — 1st
                (180, 180, 180),  # silver — 2nd
                (180, 120, 60),   # bronze — 3rd
            ]
            for ri, row in enumerate(self.leaderboard_data[:MAX_ROWS]):
                ry = hy + 22 + ri * ROW_H

                # Alternating row tint
                if ri % 2 == 0:
                    row_bg = pygame.Rect(lx + 4, ry - 2, lw - 8, ROW_H - 2)
                    pygame.draw.rect(surface, (75, 48, 18), row_bg, border_radius=4)

                rc = rank_colors[ri] if ri < 3 else TEXT_LIGHT

                # Rank number
                rank_surf = self._font_small.render(str(ri + 1), True, rc)
                surface.blit(rank_surf, (cx0, ry + 4))

                # Name
                name_surf = self._font_small.render(
                    str(row.get('player_name', ''))[:18], True, rc)
                surface.blit(name_surf, (cx1, ry + 4))

                # Wins
                wins_surf = self._font_small.render(str(row.get('wins', '')), True, rc)
                surface.blit(wins_surf, (cx2, ry + 4))

                # Avg
                avg_surf = self._font_small.render(
                    f"{row.get('avg_score', 0):.1f}", True, rc)
                surface.blit(avg_surf, (cx3, ry + 4))

                # Row separator line (skip after last row)
                if ri < min(MAX_ROWS, len(self.leaderboard_data)) - 1:
                    sep_y = ry + ROW_H - 2
                    pygame.draw.line(surface, (90, 62, 28),
                                     (lx + 14, sep_y), (lx + lw - 14, sep_y), 1)
        else:
            nd = self._font_small.render("No games played yet.", True, TEXT_LIGHT)
            surface.blit(nd, (lx + 20, hy + 30))
