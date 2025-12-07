"""UI drawing helpers used by the App controller.

This module centralizes small reusable drawing routines so higher-level
code can remain focused on game logic.
"""

import pyxel
from typing import List
from constants import BACKGROUND_COLORS, BACKGROUND_BAND_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT

def draw_background(width: int, height: int) -> None:
    colors: List[int] = BACKGROUND_COLORS
    band_height = BACKGROUND_BAND_HEIGHT

    for y in range(0, height, band_height):
        t = y / max(1, (height - 1))
        idx = int(t * (len(colors) - 1))
        color = colors[idx]
        pyxel.rect(0, y, width, band_height, color)


def draw_button(x: int, y: int, text: str, base_color: int, hover_color: int) -> None:
    hover = (x <= pyxel.mouse_x <= x + BUTTON_WIDTH and
             y <= pyxel.mouse_y <= y + BUTTON_HEIGHT)
    color = hover_color if hover else base_color
    pyxel.rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, color)

    text_x = x + (BUTTON_WIDTH - len(text) * 4) // 2
    text_y = y + (BUTTON_HEIGHT - 6) // 2
    pyxel.text(text_x, text_y, text, 0)


def draw_fruit(x: int, y: int) -> None:
    pyxel.circ(x + 8, y + 8, 6, 8)
    pyxel.circ(x + 5, y + 5, 2, 7)
    pyxel.rect(x + 7, y + 1, 2, 3, 4)


def draw_head(x: int, y: int, size: int) -> None:

    # Head base
    pyxel.rect(x, y, size, size, 6)

    # Eyes
    pyxel.rect(x + 3, y + 4, 6, 6, 7)
    pyxel.rect(x + 9, y + 4, 6, 6, 7)
    pyxel.pset(x + 5, y + 6, 0)
    pyxel.pset(x + 11, y + 6, 0)

    # Nose
    pyxel.rect(x + 6, y + 9, 4, 2, 9)
