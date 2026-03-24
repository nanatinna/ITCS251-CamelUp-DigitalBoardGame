"""
helpers.py - Utility functions for formatting and calculations.
"""
from typing import Tuple

def format_coins(amount: int) -> str:
    """Formats coin amount with a prefix, e.g., '+5' or '-3'."""
    if amount > 0:
        return f"+{amount}"
    return str(amount)

def clamp(value: int, min_val: int, max_val: int) -> int:
    """Returns value clamped between min_val and max_val."""
    return max(min_val, min(value, max_val))

def color_hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Converts a hex string like '#RRGGBB' to an RGB tuple."""
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
