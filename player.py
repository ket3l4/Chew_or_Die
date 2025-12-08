"""Player (snake) logic and drawing routines.

This module manages the player's position, direction, movement, collision,
and drawing of the body and head.
"""

import pyxel
import ui
from typing import List, Tuple
from constants import RAINBOW_COLORS


class Player:
    """Manages the snake's state and movement in the game."""
    def __init__(self, width: int, height: int, size: int, rainbow_colors: List[int] | None = None):
        """Initializes the Player object.

        Args:
            width: The screen width.
            height: The screen height.
            size: The size of one body segment (SEGMENT_SIZE).
            rainbow_colors: A list of color indices for the body segments.
        """
        self.WIDTH = width
        self.HEIGHT = height
        self.SEGMENT_SIZE = size
        # Use provided colors or the default from constants.
        self.RAINBOW_COLORS = rainbow_colors if rainbow_colors is not None else RAINBOW_COLORS

        # Initialize player body with three segments near the center.
        start_x = width // 2
        start_y = height // 2
        self.body: List[List[int]] = [
            [start_x, start_y],
            [start_x - size, start_y],
            [start_x - size * 2, start_y],
        ]

        self.direction: List[int] = [size, 0]  # Initial movement is to the right.
        self.move_counter = 0
        self.move_speed = 5  # Controls how many frames pass before the snake moves.

    def set_direction(self, d: Tuple[int, int]) -> None:
        """Sets the player's movement direction.

        Prevents instantaneous 180-degree reversal (e.g., from right to left).

        Args:
            d: A tuple (nx, ny) representing the new direction vector.
        """
        dx, dy = self.direction
        nx, ny = d
        # Check if the new direction is a direct reversal of the current direction.
        if not (nx == -dx and ny == -dy):
            self.direction = [nx, ny]

    def update_movement(self, grow: bool = False):
        """Advances the player by one step when the move speed counter is met.

        Args:
            grow: If True, the tail segment is not popped, resulting in growth.

        Returns:
            A tuple (status, head_pos) where status is one of:
            "WAIT": Not time to move yet.
            "MOVE": Player has moved one step.
            "COLLISION": Player has collided with itself.
            The head_pos is (nx, ny) only for "MOVE" and "COLLISION" status, otherwise None.
        """
        self.move_counter += 1
        if self.move_counter % self.move_speed != 0:
            return "WAIT", None

        # Calculate the next head position (nx, ny) with screen wrapping.
        x, y = self.body[0]
        dx, dy = self.direction
        nx = (x + dx) % self.WIDTH
        ny = (y + dy) % self.HEIGHT

        # Check for self-collision (collision with the body).
        # We ignore the last tail segment because it will move out of the way.
        if [nx, ny] in self.body[:-1]:
            return "COLLISION", (nx, ny)

        self.body.insert(0, [nx, ny])
        if not grow:
            self.body.pop()

        return "MOVE", (nx, ny)

    def grow_body(self) -> None:
        """Increases the snake's length by duplicating the last tail segment."""
        # Duplicates the last segment. The new segment will be properly placed
        # on the next call to update_movement (since the pop will be skipped).
        self.body.append(self.body[-1].copy())

    def draw(self, selected_character: int) -> None:
        """Draws the player: a distinct head and colored segments.

        Args:
            selected_character: An integer that could be used to select
                different drawing routines, though currently unused.
        """
        for i, (x, y) in enumerate(self.body):
            if i == 0:
                # Draw the head using the dedicated UI function.
                ui.draw_head(x, y, self.SEGMENT_SIZE)
            else:
                # Draw body segments with rainbow colors, cycling through the list.
                # Use (i - 1) to start the color cycle index at 0 for the first body segment.
                color = self.RAINBOW_COLORS[(i - 1) % len(self.RAINBOW_COLORS)]
                pyxel.rect(x, y, self.SEGMENT_SIZE, self.SEGMENT_SIZE, color)
