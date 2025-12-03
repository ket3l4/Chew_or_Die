"""Manage falling dots (obstacles) used by the main game.

The DotManager spawns dots, updates their positions, handles collisions
with the player head, and exposes simple tuning via difficulty().
"""

import pyxel
import random
import math
from constants import WIDTH, HEIGHT, BASE_C_REAL

class DotManager:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        self.dots = []
        self.dot_radius = 4
        self.dot_spawn_interval = 16
        self.difficulty_level = 0

    def difficulty(self, score, target_c_real, target_c_imag):
        # distance from baseline complex constant
        D = math.hypot(target_c_real - BASE_C_REAL, target_c_imag)

        # scale D to an integer factor for radius and spawn reduction
        scale = int(D * 10)

        # dot radius grows with distance but is clamped to 3
        self.dot_radius = min(3, 1 + scale)

        # difficulty level from score (each 30 points increases level)
        self.difficulty_level = score // 30

        # base spawn interval reduced by difficulty level and further reduced
        # by a distance-proportional amount; clamp to minimum of 2
        base_interval = max(6, 16 - self.difficulty_level * 2)
        reduction = int(D * 25)  # equivalent to previous scale_factor * 2.5
        self.dot_spawn_interval = max(2, base_interval - reduction)

    def update_dots(self, score):
        # Spawn new dot periodically once the player has at least 10 score
        if score >= 10 and pyxel.frame_count % self.dot_spawn_interval == 0:
            speed = random.uniform(1.0, 3.0)
            color = random.randint(2, 15)
            base_x = random.randint(0, self.WIDTH - 1)
            # horizontal position oscillates slightly for variety
            x = (base_x + math.sin(pyxel.frame_count * 0.1) * 20) % self.WIDTH
            # dot stored as [y, speed, color, sliced_flag, base_x, x]
            self.dots.append([0.0, speed, color, 0, base_x, x])

        # Update each dot's position and remove dots that have fallen off
        updated = []
        for y, speed, color, sliced, base_x, x in self.dots:
            cur_speed = speed * (6 if sliced else 1)
            y += cur_speed
            x = (base_x + math.sin(pyxel.frame_count * 0.1) * 20) % self.WIDTH
            if y < self.HEIGHT:
                updated.append([y, speed, color, sliced, base_x, x])
        self.dots = updated

    def check_collision(self, head_x, head_y, size):
        left = head_x
        top = head_y
        right = head_x + size
        bottom = head_y + size

        hit = False
        for i in range(len(self.dots)):
            y, speed, color, sliced, base_x, x = self.dots[i]
            if sliced:
                continue
            r = self.dot_radius
            if (left < x + r and right > x - r and
                    top < y + r and bottom > y - r):
                self.dots[i][3] = 1
                hit = True

        return -1 if hit else 0

    def draw(self):
        for y, speed, color, sliced, base_x, x in self.dots:
            if not sliced:
                pyxel.circ(int(x), int(y), self.dot_radius, color)
            else:
                pyxel.pset(int(x - 1), int(y - 1), color)
                pyxel.pset(int(x + 1), int(y + 1), color)
