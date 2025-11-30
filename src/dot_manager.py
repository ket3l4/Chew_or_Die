import pyxel
import random
import math
from constants import WIDTH, HEIGHT, BASE_C_REAL

class DotManager:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        self.dots = []
        self.dot_radius = 2
        self.dot_spawn_interval = 16
        self.difficulty_level = 0

    def difficulty(self, score, target_c_real, target_c_imag):
        D = math.sqrt((target_c_real - BASE_C_REAL) ** 2 +
                      (target_c_imag - 0.0) ** 2)
        scale_factor = D * 10

        self.dot_radius = min(3, 1 + int(scale_factor))

        self.difficulty_level = score // 30
        base_interval = max(6, 16 - self.difficulty_level * 2)
        self.dot_spawn_interval = max(2, base_interval - int(scale_factor * 2.5))

    def update_dots(self, score):
        if score >= 10 and pyxel.frame_count % self.dot_spawn_interval == 0:
            speed = random.uniform(1.0, 3.0)
            color = random.randint(2, 15)
            base_x = random.randint(0, self.WIDTH - 1)
            x = (base_x + math.sin(pyxel.frame_count * 0.1) * 20) % self.WIDTH
            self.dots.append([0.0, speed, color, 0, base_x, x])

        new_list = []
        for y, speed, color, sliced, base_x, x in self.dots:
            cur_speed = speed * (6 if sliced else 1)
            y += cur_speed

            x = (base_x + math.sin(pyxel.frame_count * 0.1) * 20) % self.WIDTH

            if y < self.HEIGHT:
                new_list.append([y, speed, color, sliced, base_x, x])
        self.dots = new_list

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
