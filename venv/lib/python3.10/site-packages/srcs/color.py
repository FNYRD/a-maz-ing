import random
from enum import IntEnum


class Color(IntEnum):
    """Class containing prefedined color values for the maze."""

    # Dark & Moody
    CHARCOAL = 0xFF1a1a1a
    DEEP_NAVY = 0xFF0a1428
    DARK_SLATE = 0xFF2c3e50

    # Rich Jewel Tones
    EMERALD = 0xFF27ae60
    SAPPHIRE = 0xFF2980b9
    AMETHYST = 0xFF8e44ad
    RUBY = 0xFFc0392b

    # Vibrant & Bold
    NEON_CYAN = 0xFF00d4ff
    NEON_MAGENTA = 0xFFff00ff
    NEON_LIME = 0xFF00ff41
    NEON_ORANGE = 0xFFff6600

    # Elegant Neutrals
    GRANITE = 0xFF555555
    GUNMETAL = 0xFF2f4f4f
    PEWTER = 0xFF708090

    # Atmospheric
    MIDNIGHT = 0xFF0f0f1e
    FOREST = 0xFF1b4332
    PLUM = 0xFF44355b
    TEAL = 0xFF0d5f5f

    # Basic
    RED = 0xFFFF0000
    GREEN = 0xFF00FF00
    BLUE = 0xFF0000FF
    BLACK = 0xFF000000
    WHITE = 0xFFFFFFFF

    # Default
    BG = 0xff113355
    WALL = 0xeeeeeeff
    HL = 0xFF00FFFF
    PATH = 0xff888888

    @classmethod
    def get_random_color(cls) -> int:
        """method that returns a random color from the class"""
        return random.choice(list(Color)[:-4])
