"""Julia set fractal rendering and chew-mini-game logic.

This module renders a reduced-resolution Julia set and exposes methods to
manage the chewing mini-game (timing, input, and win/lose detection).
The goal of the mini-game is to match a complex constant (C) by mouse and keys.
"""

import pyxel
import random
import math
from constants import (MAX_ITER, BASE_C_REAL, BASE_C_IMAG, CHEWING_TIME_SECONDS,
                       FRACTAL_MIN_X, FRACTAL_MAX_X, FRACTAL_MIN_Y, FRACTAL_MAX_Y,
                       WINNING_TOLERANCE, JULIA_RENDER_STEP, PALETTE_WRAP, PALETTE_OFFSET,
                       CHEW_TIMER_DECREMENT)

class Julia_set:
    """Manages the Julia set rendering and the chewing mini-game state."""
    def __init__(self, width, height, fps, dot_manager):
        """Initializes the Julia_set object.

        Args:
            width: The screen width.
            height: The screen height.
            fps: The game frames per second.
            dot_manager: The DotManager instance for difficulty scaling.
        """
        self.WIDTH = width
        self.HEIGHT = height
        self.FPS = fps
        self.dm = dot_manager  # Reference to DotManager for setting difficulty.

        # Target C to be matched by the player.
        self.target_c_real = 0.0
        self.target_c_imag = 0.0
        self.target_c = complex(0.0, 0.0)

        # Player-controlled C (real and imaginary parts, and the complex value).
        self.c_real = 0.0
        self.c_imag = 0.0
        self.c_fixed = complex(0.0, 0.0)

        self.chew_timer = 0  # Countdown timer for the mini-game.
        self.input_delay = 0  # Frame counter to debounce keyboard input.

    def start_timer(self):
        """Starts the countdown timer for the chewing mini-game."""
        self.chew_timer = CHEWING_TIME_SECONDS * self.FPS

    def reset_target_c(self, score):
        """Sets a new random target complex constant (C) and resets the player C.

        The target C is set near the BASE_C constants with a small random offset.

        Args:
            score: The player's current score, used for dot difficulty.
        """
        # Random offsets for the target C components.
        r = random.uniform(-0.15, 0.15)
        im = random.uniform(-0.15, 0.15)

        self.target_c_real = round(BASE_C_REAL + r, 2)
        self.target_c_imag = round(BASE_C_IMAG + im, 2)
        self.target_c = complex(self.target_c_real, self.target_c_imag)

        # Update dot difficulty based on the new target C.
        self.dm.difficulty(score, self.target_c_real, self.target_c_imag)

        # Reset player-controlled C.
        self.c_real = 0.0
        self.c_imag = 0.0
        self.c_fixed = complex(0.0, 0.0)

    def julia_iter(self, z: complex, c: complex) -> int:
        """Performs the Julia set iteration for a single point.

        Calculates the number of iterations before the absolute value of z
        exceeds 2.

        Args:
            z: The initial complex number in the Z-plane.
            c: The fixed complex constant (the player's control point).

        Returns:
            The number of iterations before divergence, or MAX_ITER if it did not diverge.
        """
        n = 0
        while abs(z) <= 2 and n < MAX_ITER:
            z = z * z + c
            n += 1
        return n

    def update_chewing(self):
        """Updates the chewing mini-game logic (timer, input, and win condition).

        Returns:
            A string indicating the game status: "LOSE", "WIN", or "CONTINUE".
        """
        self.chew_timer -= CHEW_TIMER_DECREMENT
        # When the chewing timer reaches zero, indicate a timeout rather
        # than forcing a direct "LOSE" string. The caller (`main.py`) will
        # apply the penalty and decide whether the game ends.
        if self.chew_timer <= 0:
            return "TIMEOUT"

        # Update C components based on mouse position for a primary control method.
        # Maps screen coordinates (0 to WIDTH/HEIGHT) to a range of approx -1 to 1.
        self.c_real = (pyxel.mouse_x / self.WIDTH) * 2 - 1
        self.c_imag = (pyxel.mouse_y / self.HEIGHT) * 2 - 1

        # Update the final complex constant used for the fractal drawing.
        self.c_fixed = complex(self.c_real, self.c_imag)

        # Check for win condition: distance between current C and target C.
        dr = self.c_real - self.target_c_real
        di = self.c_imag - self.target_c_imag
        dist = math.sqrt(dr * dr + di * di)

        if dist < WINNING_TOLERANCE:
            return "WIN"

        return "CONTINUE"

    def draw_fractal(self):
        """Renders the Julia set fractal using the current fixed complex constant (C).

        The fractal is drawn at a reduced 2x2 pixel block resolution for performance.
        """
        # Calculate scaling factors to map screen pixels to complex plane coordinates.
        scale_x = (FRACTAL_MAX_X - FRACTAL_MIN_X) / self.WIDTH
        scale_y = (FRACTAL_MAX_Y - FRACTAL_MIN_Y) / self.HEIGHT

        # Draw at reduced-resolution pixel blocks for performance.
        step = JULIA_RENDER_STEP
        for x_pixel in range(0, self.WIDTH, step):
            # Calculate the real part corresponding to the x_pixel.
            real = FRACTAL_MIN_X + x_pixel * scale_x
            for y_pixel in range(0, self.HEIGHT, step):
                # Calculate the imaginary part corresponding to the y_pixel.
                imag = FRACTAL_MIN_Y + y_pixel * scale_y
                # Calculate the iteration count for the point.
                iter_count = self.julia_iter(complex(real, imag), self.c_fixed)
                # Determine color: 0 for MAX_ITER (inside the set), otherwise a colored pattern.
                color = 0 if iter_count == MAX_ITER else (iter_count % PALETTE_WRAP) + PALETTE_OFFSET

                # Draw the 2x2 pixel block with the determined color.
                pyxel.pset(x_pixel, y_pixel, color)
                pyxel.pset(x_pixel + 1, y_pixel, color)
                pyxel.pset(x_pixel, y_pixel + 1, color)
                pyxel.pset(x_pixel + 1, y_pixel + 1, color)

        # --- HUD overlay showing current/target C and remaining time ---
        pyxel.rect(0, 0, self.WIDTH, 24, 0)
        pyxel.text(4, 4, f"CURRENT C: {self.c_real:.2f} + {self.c_imag:.2f}i", 7)
        # Display time remaining.
        pyxel.text(self.WIDTH - 70, 4, f"TIME: {self.chew_timer // self.FPS}", 9)
        # Display the target C.
        pyxel.text(4, 14, f"TARGET C: {self.target_c_real:.2f} + {self.target_c_imag:.2f}i", 10)
        pyxel.text(200, 9, "CHEW YOUR FOOD, MOVE MOUSE TO MATCH THE TARGET C!!", 15)