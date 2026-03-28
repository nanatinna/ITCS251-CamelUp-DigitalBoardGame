import pygame
import math
from typing import Dict, List, Optional, Tuple

from gui.theme import (
    SAND_LIGHT, SAND_DARK, WOOD_DARK, WOOD_MID, WOOD_LIGHT,
    TEXT_DARK, TEXT_LIGHT, GOLD, CAMEL_COLOR_MAP,
    CAMEL_W, CAMEL_H, CAMEL_STACK_OFFSET, TILE_SIZE,
    CENTER_W, MAIN_H, WHITE, RED, load_font,
)
from gui.components.camel_sprite import CamelSprite
from game.models import CAMEL_COLORS, CRAZY_CAMEL_COLORS, ALL_CAMEL_COLORS


class Board:
    """Renders the 16-tile oval desert race track with stacked camels."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tile_positions: Dict[int, Tuple[int, int]] = self._calculate_tile_positions()
        # Sprites for all 7 camels (5 racing + 2 crazy)
        self.camel_sprites: Dict[str, CamelSprite] = {
            color: CamelSprite(color) for color in ALL_CAMEL_COLORS
        }
        self._font_small = None
        self._font_medium = None
        self._tile_select_mode = False
        self._valid_tiles: List[int] = []
        self._hovered_tile: Optional[int] = None

    # ------------------------------------------------------------------ fonts
    def _get_fonts(self):
        if self._font_small is None:
            self._font_small = load_font(11)
            self._font_medium = load_font(13)

    # -------------------------------------------------------- tile positions
    def _calculate_tile_positions(self) -> Dict[int, Tuple[int, int]]:
        """
        Pre-calculate centre (x, y) for tiles 1-16 arranged clockwise around
        a clean rectangle.

        Corner tiles (shared by two edges):
          Tile  1 = top-left     Tile  5 = top-right
          Tile 10 = bottom-right  Tile 14 = bottom-left

        Edges:
          Top    (1-5):   left → right   (5 tiles, corners included)
          Right  (6-9):   top → bottom   (4 tiles, corners excluded)
          Bottom (10-14): right → left   (5 tiles, corners included)
          Left   (15-16): bottom → top   (2 tiles, corners excluded)
        """
        half = TILE_SIZE // 2           # 35 px
        margin = 50

        # Absolute screen coordinates of the four track corners
        x_l = self.x + margin + half      # left  column  x
        x_r = self.x + self.width  - margin - half   # right column  x
        y_t = self.y + margin + half      # top   row     y
        y_b = self.y + self.height - margin - half   # bottom row    y

        tw = x_r - x_l      # horizontal span between corner centres
        th = y_b - y_t      # vertical   span between corner centres

        positions: Dict[int, Tuple[int, int]] = {}

        # ── Top row: tiles 1-5 (left to right, tw / 4 spacing) ──────────────
        for i, tile in enumerate(range(1, 6)):
            positions[tile] = (round(x_l + i * tw / 4), y_t)

        # ── Right col: tiles 6-9 (top to bottom, th / 5 spacing) ────────────
        # i = 0..3  →  segment 1..4 out of 5  (corners are segment 0 and 5)
        for i, tile in enumerate(range(6, 10)):
            positions[tile] = (x_r, round(y_t + (i + 1) * th / 5))

        # ── Bottom row: tiles 10-14 (right to left, tw / 4 spacing) ─────────
        for i, tile in enumerate(range(10, 15)):
            positions[tile] = (round(x_r - i * tw / 4), y_b)

        # ── Left col: tiles 15-16 (bottom to top, th / 3 spacing) ───────────
        # i = 0..1  →  segment 1..2 out of 3  (corners are segment 0 and 3)
        for i, tile in enumerate(range(15, 17)):
            positions[tile] = (x_l, round(y_b - (i + 1) * th / 3))

        return positions

    # --------------------------------------------------------------- helpers
    def get_tile_rect(self, tile_num: int) -> pygame.Rect:
        cx, cy = self.tile_positions.get(tile_num, (0, 0))
        return pygame.Rect(cx - TILE_SIZE // 2, cy - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)

    def set_tile_select_mode(self, active: bool, valid_tiles: List[int] = None):
        self._tile_select_mode = active
        self._valid_tiles = valid_tiles or []
        if not active:
            self._hovered_tile = None

    def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
        if not self._tile_select_mode:
            self._hovered_tile = None
            return
        self._hovered_tile = None
        for tile_num in self._valid_tiles:
            if self.get_tile_rect(tile_num).collidepoint(mouse_pos):
                self._hovered_tile = tile_num
                break

    def get_clicked_tile(self, mouse_pos: Tuple[int, int]) -> Optional[int]:
        for tile_num in self._valid_tiles:
            if self.get_tile_rect(tile_num).collidepoint(mouse_pos):
                return tile_num
        return None

    def animate_camel_move(self, color: str, new_tile: int):
        if new_tile in self.tile_positions:
            target = self.tile_positions[new_tile]
            sprite = self.camel_sprites[color]
            start = sprite.pos if sprite.pos != (0.0, 0.0) else (float(target[0]), float(target[1]))
            sprite.start_animation(start, (float(target[0]), float(target[1])))

    @property
    def is_animating(self) -> bool:
        return any(s.is_animating for s in self.camel_sprites.values())

    def update(self):
        for sprite in self.camel_sprites.values():
            sprite.update()

    # --------------------------------------------------------------- drawing
    def draw(self, surface: pygame.Surface, game_state):
        self._get_fonts()

        # Board background
        board_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, SAND_LIGHT, board_rect, border_radius=12)
        pygame.draw.rect(surface, WOOD_MID, board_rect, width=3, border_radius=12)

        # Track path connecting tiles
        self._draw_track_path(surface)

        # Tiles
        for tile_num in range(1, 17):
            self._draw_tile(surface, tile_num, game_state)

        # Camels
        self._draw_all_camels(surface, game_state)

    def _draw_track_path(self, surface: pygame.Surface):
        """Draw the racetrack as a clean rounded rectangle outline."""
        half = TILE_SIZE // 2
        margin = 50
        rect = pygame.Rect(
            self.x + margin,
            self.y + margin,
            self.width  - 2 * margin,
            self.height - 2 * margin,
        )
        # Outer shadow
        pygame.draw.rect(surface, SAND_DARK,
                         rect.inflate(10, 10), width=8, border_radius=18)
        # Main track border
        pygame.draw.rect(surface, (180, 150, 100),
                         rect, width=5, border_radius=14)

    def _draw_tile(self, surface: pygame.Surface, tile_num: int, game_state):
        if tile_num not in self.tile_positions:
            return
        rect = self.get_tile_rect(tile_num)

        if self._tile_select_mode and tile_num in self._valid_tiles:
            fill   = (180, 230, 160) if self._hovered_tile != tile_num else (130, 205, 110)
            border = (40, 160, 40)
            border_w = 3
        else:
            fill     = (226, 198, 150)   # slightly darker than board bg → visible separation
            border   = WOOD_MID
            border_w = 2

        pygame.draw.rect(surface, fill,   rect, border_radius=10)
        pygame.draw.rect(surface, border, rect, width=border_w, border_radius=10)

        # Tile number (top-left corner)
        num_surf = self._font_small.render(str(tile_num), True, TEXT_DARK)
        surface.blit(num_surf, (rect.x + 4, rect.y + 3))

        # Desert marker
        if game_state:
            dt = game_state.desert_tiles.get(tile_num)
            if dt:
                dtype = dt.get('type', dt) if isinstance(dt, dict) else dt
                if dtype == 'oasis':
                    self._draw_oasis_icon(surface, rect)
                elif dtype == 'mirage':
                    self._draw_mirage_icon(surface, rect)

        # Finish-line marker on tile 16
        if tile_num == 16:
            fin = self._font_small.render("FIN", True, GOLD)
            surface.blit(fin, (rect.x + 2, rect.bottom - 14))

    def _draw_oasis_icon(self, surface: pygame.Surface, r: pygame.Rect):
        cx, cy = r.centerx, r.centery + 6
        pygame.draw.rect(surface, (120, 80, 30), pygame.Rect(cx - 2, cy - 6, 4, 10))
        pygame.draw.circle(surface, (34, 139, 34), (cx, cy - 10), 7)
        pygame.draw.circle(surface, (34, 139, 34), (cx - 6, cy - 6), 5)
        pygame.draw.circle(surface, (34, 139, 34), (cx + 6, cy - 6), 5)
        lbl = self._font_small.render("+1", True, (0, 140, 0))
        surface.blit(lbl, (cx - 6, cy + 4))

    def _draw_mirage_icon(self, surface: pygame.Surface, r: pygame.Rect):
        cx, cy = r.centerx, r.centery + 8
        pts = [(cx - 10 + i, cy + int(math.sin(i * 0.7) * 3)) for i in range(20)]
        if len(pts) > 1:
            pygame.draw.lines(surface, RED, False, pts, 2)
        lbl = self._font_small.render("-1", True, RED)
        surface.blit(lbl, (cx - 6, cy + 5))

    def _draw_all_camels(self, surface: pygame.Surface, game_state):
        if not game_state:
            return

        tile_camels: Dict[int, list] = {}
        for camel in game_state.camels:
            if camel.position > 0:
                tile_camels.setdefault(camel.position, []).append(camel)

        for tile_num, camels in tile_camels.items():
            if tile_num not in self.tile_positions:
                continue
            camels_sorted = sorted(camels, key=lambda c: c.stack_order)
            tile_rect = self.get_tile_rect(tile_num)
            base_x = tile_rect.centerx - CAMEL_W // 2
            base_y = tile_rect.bottom - CAMEL_H - 4

            for i, camel in enumerate(camels_sorted):
                dx = base_x
                dy = base_y - i * CAMEL_STACK_OFFSET
                sprite = self.camel_sprites[camel.color]
                if sprite.is_animating:
                    sprite.draw(surface)
                else:
                    sprite.draw(surface, dx, dy)
                    sprite.pos = (float(dx), float(dy))
                    sprite.target_pos = sprite.pos

                # Draw ← indicator on crazy camels so the player can see direction
                if camel.is_crazy and not sprite.is_animating:
                    arrow_surf = self._font_small.render("←", True, (240, 90, 90))
                    surface.blit(arrow_surf, (dx + CAMEL_W - 2, dy - 2))
