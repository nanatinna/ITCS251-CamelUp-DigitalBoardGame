"""
settings.py - Global constants for Camel Up.
"""

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "BACKGROUND": (240, 230, 210),  # Sandy color
    "CAMEL_WHITE": (245, 245, 245),
    "CAMEL_ORANGE": (255, 140, 0),
    "CAMEL_GREEN": (76, 175, 80),
    "CAMEL_BLUE": (33, 150, 243),
    "CAMEL_YELLOW": (255, 215, 0),
    "TEXT": (50, 50, 50),
    "ERROR": (220, 50, 50),
    "PANEL": (255, 255, 255),
    "BUTTON": (200, 200, 200),
    "BUTTON_HOVER": (170, 170, 170),
    "BUTTON_DISABLED": (220, 220, 220),
    "HIGHLIGHT": (255, 255, 100, 128),
    "DESERT_PLUS": (100, 200, 100),
    "DESERT_MINUS": (200, 100, 100),
}

# Fonts
FONT_NAME = "arial"  # Pygame sysfont fallback

# Gameplay constants
TRACK_LENGTH = 16
NUM_CAMELS = 5
CAMEL_COLORS = ["White", "Orange", "Green", "Blue", "Yellow"]
MAX_PLAYERS = 5
MIN_PLAYERS = 2

# Dimensions
BOARD_X = 50
BOARD_Y = 50
BOARD_WIDTH = 500
BOARD_HEIGHT = 500

SIDEBAR_X = 600
SIDEBAR_Y = 50
SIDEBAR_WIDTH = 350
SIDEBAR_HEIGHT = 650
