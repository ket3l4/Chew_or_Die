import pyxel
import ui
from typing import List, Tuple
from constants import RAINBOW_COLORS


class Player:
    def __init__(self, width: int, height: int, size: int, rainbow_colors: List[int] | None = None):
        self.WIDTH = width
        self.HEIGHT = height
        self.SEGMENT_SIZE = size
        self.RAINBOW_COLORS = rainbow_colors if rainbow_colors is not None else RAINBOW_COLORS

        start_x = width // 2
        start_y = height // 2
        self.body: List[List[int]] = [
            [start_x, start_y],
            [start_x - size, start_y],
            [start_x - size * 2, start_y],
        ]

        self.direction: List[int] = [size, 0]
        self.move_counter = 0
        self.move_speed = 5

    def set_direction(self, d: Tuple[int, int]) -> None:
        """Set movement direction unless it's a 180° reversal."""
        dx, dy = self.direction
        nx, ny = d
        if not (nx == -dx and ny == -dy):
            self.direction = [nx, ny]

    def update_movement(self, grow: bool = False):
        """Advance the player by one step when move counter reaches speed.

        Returns a tuple (status, head_pos) where status is one of
        "WAIT", "MOVE", or "COLLISION".
        """
        self.move_counter += 1
        if self.move_counter % self.move_speed != 0:
            return "WAIT", None

        x, y = self.body[0]
        dx, dy = self.direction
        nx = (x + dx) % self.WIDTH
        ny = (y + dy) % self.HEIGHT

        # self-collision (ignore last tail segment because it will move)
        if [nx, ny] in self.body[:-1]:
            return "COLLISION", (nx, ny)

        self.body.insert(0, [nx, ny])
        if not grow:
            self.body.pop()

        return "MOVE", (nx, ny)

    def grow_body(self) -> None:
        """Grow by duplicating the last segment."""
        self.body.append(self.body[-1].copy())

    def draw(self, selected_character: int) -> None:
        """Draw the player: a distinct head and colored segments."""
        for i, (x, y) in enumerate(self.body):
            if i == 0:
                ui.draw_head(x, y, self.SEGMENT_SIZE)
            else:
                color = self.RAINBOW_COLORS[(i - 1) % len(self.RAINBOW_COLORS)]
                pyxel.rect(x, y, self.SEGMENT_SIZE, self.SEGMENT_SIZE, color)
