"""Julia set fractal rendering and chew-mini-game logic.

This module renders a reduced-resolution Julia set and exposes methods to
manage the chewing mini-game (timing, input, and win/lose detection).
"""

import pyxel
import random
import math
from typing import Tuple
from constants import (MAX_ITER, BASE_C_REAL, BASE_C_IMAG, CHEWING_TIME_SECONDS,
                       FRACTAL_MIN_X, FRACTAL_MAX_X, FRACTAL_MIN_Y, FRACTAL_MAX_Y)

class Julia_set:
    def __init__(self, width, height, fps, dot_manager):
        self.WIDTH = width
        self.HEIGHT = height
        self.FPS = fps
        self.dm = dot_manager

        self.target_c_real = 0
        self.target_c_imag = 0
        self.target_c = 0

        self.c_real = 0
        self.c_imag = 0
        self.c_fixed = 0

        self.chew_timer = 0
        self.input_delay = 0

    def start_timer(self):
        self.chew_timer = CHEWING_TIME_SECONDS * self.FPS

    def reset_target_c(self, score):
        r = random.uniform(-0.15, 0.15)
        im = random.uniform(-0.15, 0.15)

        self.target_c_real = round(BASE_C_REAL + r, 2)
        self.target_c_imag = round(BASE_C_IMAG + im, 2)
        self.target_c = complex(self.target_c_real, self.target_c_imag)

        self.dm.difficulty(score, self.target_c_real, self.target_c_imag)

        self.c_real = 0
        self.c_imag = 0
        self.c_fixed = 0

    def julia_iter(self, z, c):
        n = 0
        while abs(z) <= 2 and n < MAX_ITER:
            z = z * z + c
            n += 1
        return n

    def update_chewing(self):
        self.chew_timer -= 1
        if self.chew_timer <= 0:
            return "LOSE"

        self.c_real = (pyxel.mouse_x / self.WIDTH) * 2 - 1
        self.c_imag = (pyxel.mouse_y / self.HEIGHT) * 2 - 1

        fine = 0.01
        coarse = 0.1
        step = coarse if pyxel.btn(pyxel.KEY_SHIFT) else fine

        if self.input_delay == 0:
            if pyxel.btn(pyxel.KEY_LEFT):
                self.c_real -= step
            if pyxel.btn(pyxel.KEY_RIGHT):
                self.c_real += step
            if pyxel.btn(pyxel.KEY_UP):
                self.c_imag -= step
            if pyxel.btn(pyxel.KEY_DOWN):
                self.c_imag += step
            self.input_delay = 3

        if self.input_delay > 0:
            self.input_delay -= 1

        self.c_fixed = complex(self.c_real, self.c_imag)

        dr = self.c_real - self.target_c_real
        di = self.c_imag - self.target_c_imag
        dist = math.sqrt(dr * dr + di * di)

        if dist < 0.02:
            return "WIN"

        return "CONTINUE"

    def draw_fractal(self):
        # Map pixels to complex plane coordinates
        scale_x = (FRACTAL_MAX_X - FRACTAL_MIN_X) / self.WIDTH
        scale_y = (FRACTAL_MAX_Y - FRACTAL_MIN_Y) / self.HEIGHT

        # Draw at 2x2 pixel blocks for performance
        step = 2
        for x_pixel in range(0, self.WIDTH, step):
            real = FRACTAL_MIN_X + x_pixel * scale_x
            for y_pixel in range(0, self.HEIGHT, step):
                imag = FRACTAL_MIN_Y + y_pixel * scale_y
                iter_count = self.julia_iter(complex(real, imag), self.c_fixed)
                color = 0 if iter_count == MAX_ITER else (iter_count % 14) + 2

                pyxel.pset(x_pixel, y_pixel, color)
                pyxel.pset(x_pixel + 1, y_pixel, color)
                pyxel.pset(x_pixel, y_pixel + 1, color)
                pyxel.pset(x_pixel + 1, y_pixel + 1, color)

        # HUD overlay showing current/target C and remaining time
        pyxel.rect(0, 0, self.WIDTH, 24, 0)
        pyxel.text(4, 4, f"CURRENT C: {self.c_real:.2f} + {self.c_imag:.2f}i", 7)
        pyxel.text(self.WIDTH - 70, 4, f"TIME: {self.chew_timer // self.FPS}", 9)
        pyxel.text(4, 14, f"TARGET C: {self.target_c_real:.2f} + {self.target_c_imag:.2f}i", 10)
        pyxel.text(200, 9, "CHEW YOUR FOOD, MOVE MOUSE TO MATCH THE TARGET C!!", 15)
