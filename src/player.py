import pyxel
from constants import RAINBOW_COLORS

class Player:
    def __init__(self, width, height, size, rainbow_colors=None):
        self.WIDTH = width
        self.HEIGHT = height
        self.SEGMENT_SIZE = size
        self.RAINBOW_COLORS = rainbow_colors if rainbow_colors is not None else RAINBOW_COLORS

        start_x = width // 2
        start_y = height // 2
        self.body = [
            [start_x, start_y],
            [start_x - size, start_y],
            [start_x - size * 2, start_y]
        ]

        self.direction = [size, 0]
        self.move_counter = 0
        self.move_speed = 5

    def set_direction(self, d):
        dx, dy = self.direction
        nx, ny = d
        if not (nx == -dx and ny == -dy):
            self.direction = d

    def update_movement(self, grow=False):
        self.move_counter += 1
        if self.move_counter % self.move_speed != 0:
            return "WAIT", None

        x, y = self.body[0]
        dx, dy = self.direction
        nx = (x + dx) % self.WIDTH
        ny = (y + dy) % self.HEIGHT

        if [nx, ny] in self.body[:-1]:
            return "COLLISION", (nx, ny)

        self.body.insert(0, [nx, ny])
        if not grow:
            self.body.pop()

        return "MOVE", (nx, ny)

    def grow_body(self):
        self.body.append(self.body[-1].copy())

    def draw(self, selected_character):
        for i, (x, y) in enumerate(self.body):
            if i == 0:
                # Cat head base
                pyxel.rect(x, y, self.SEGMENT_SIZE, self.SEGMENT_SIZE, 10)  # yellow-brown

                # Ears
                pyxel.tri(x, y, x + 5, y - 5, x + 10, y, 8)  # left ear
                pyxel.tri(x + self.SEGMENT_SIZE - 10, y, x + self.SEGMENT_SIZE - 5, y - 5, x + self.SEGMENT_SIZE, y, 8)  # right ear

                # Eyes
                pyxel.rect(x + 3, y + 4, 4, 4, 7)  # left eye white
                pyxel.rect(x + 9, y + 4, 4, 4, 7)  # right eye white
                pyxel.pset(x + 5, y + 6, 0)       # left pupil
                pyxel.pset(x + 11, y + 6, 0)      # right pupil

                # Nose
                pyxel.rect(x + 6, y + 9, 4, 2, 9)

            else:
                color = self.RAINBOW_COLORS[(i - 1) % len(self.RAINBOW_COLORS)]
                pyxel.rect(x, y, self.SEGMENT_SIZE, self.SEGMENT_SIZE, color)
