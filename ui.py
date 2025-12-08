"""UI drawing helpers used by the App controller.

This module centralizes small reusable drawing routines so higher-level
code can remain focused on game logic. It relies on the global pyxel state.
"""

import pyxel
from typing import List
from constants import BACKGROUND_COLORS, BACKGROUND_BAND_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT

def draw_background(width: int, height: int) -> None:
    """Draws a vertical gradient background using defined colors.

    The color changes gradually based on the vertical position (y-coordinate).

    Args:
        width: The width of the screen.
        height: The height of the screen.
    """
    colors: List[int] = BACKGROUND_COLORS
    band_height = BACKGROUND_BAND_HEIGHT

    for y in range(0, height, band_height):
        # Calculate a normalized value 't' (0.0 to 1.0) for the current y position.
        t = y / max(1, (height - 1))
        # Map 't' to an index in the color list.
        idx = int(t * (len(colors) - 1))
        color = colors[idx]
        pyxel.rect(0, y, width, band_height, color)


def draw_button(x: int, y: int, text: str, base_color: int, hover_color: int) -> None:
    """Draws a button, changing color when the mouse hovers over it.

    Args:
        x: The X coordinate of the top-left corner of the button.
        y: The Y coordinate of the top-left corner of the button.
        text: The text string to display on the button.
        base_color: The color index to use when the button is not hovered.
        hover_color: The color index to use when the mouse is hovering over the button.
    """
    # Check if the mouse cursor is within the button boundaries.
    hover = (x <= pyxel.mouse_x <= x + BUTTON_WIDTH and
             y <= pyxel.mouse_y <= y + BUTTON_HEIGHT)
    color = hover_color if hover else base_color
    pyxel.rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, color)

    # Calculate the position to center the text on the button.
    # Text width is length * 4 pixels.
    text_x = x + (BUTTON_WIDTH - len(text) * 4) // 2
    # Text height is 6 pixels.
    text_y = y + (BUTTON_HEIGHT - 6) // 2
    pyxel.text(text_x, text_y, text, 0) # Text color is always 0 (black/dark)


def draw_fruit(x: int, y: int) -> None:
    """Draws the fruit (food) on the screen as a simple circle with a stem.

    Args:
        x: The X coordinate of the top-left corner of the fruit's segment.
        y: The Y coordinate of the top-left corner of the fruit's segment.
    """
    # Main fruit body (large circle, color 8)
    pyxel.circ(x + 8, y + 8, 6, 8)
    # Highlight/shine (small circle, color 7)
    pyxel.circ(x + 5, y + 5, 2, 7)
    # Stem (small rectangle, color 4)
    pyxel.rect(x + 7, y + 1, 2, 3, 4)


def draw_head(x: int, y: int, size: int) -> None:
    """Draws the player's head with a distinct face.

    Args:
        x: The X coordinate of the top-left corner of the head segment.
        y: The Y coordinate of the top-left corner of the head segment.
        size: The side length of the head segment (e.g., SEGMENT_SIZE).
    """

    # Head base (square, color 6)
    pyxel.rect(x, y, size, size, 6)

    # Eyes (white rectangles, color 7)
    pyxel.rect(x + 3, y + 4, 6, 6, 7)
    pyxel.rect(x + 9, y + 4, 6, 6, 7)
    # Pupils (black pixels, color 0)
    pyxel.pset(x + 5, y + 6, 0)
    pyxel.pset(x + 11, y + 6, 0)

    # Nose (orange/brown rectangle, color 9)
    pyxel.rect(x + 6, y + 9, 4, 2, 9)
