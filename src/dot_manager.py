"""Manage falling dots (obstacles) used by the main game.

The DotManager spawns dots, updates their positions, handles collisions
with the player head, and exposes simple tuning via difficulty().
"""

import pyxel
import random
import math
import constants


class DotManager:
    """Manages the generation, movement, and collision of falling obstacle dots."""

    def __init__(self, width, height):
        """Initializes the DotManager.

        Args:
            width: The screen width.
            height: The screen height.
        """
        self.WIDTH = width
        self.HEIGHT = height
        # List of dots, where each dot is stored as:
        # [y, speed, color, sliced_flag, base_x, x]
        self.dots = []
        self.dot_radius = constants.DOT_INITIAL_RADIUS
        self.dot_spawn_interval = constants.DOT_BASE_SPAWN_INTERVAL
        self.difficulty_level = 0

    def difficulty(self, score, target_c_real, target_c_imag):
        """Scales dot properties based on score and the Julia set target C.

        Higher distance from BASE_C_REAL increases dot radius and spawn rate.

        Args:
            score: The player's current score.
            target_c_real: The real part of the Julia set target C.
            target_c_imag: The imaginary part of the Julia set target C (unused).
        """
        # Calculate the Euclidean distance from the difficulty baseline C.
        D = math.hypot(target_c_real - constants.BASE_C_REAL, target_c_imag)

        # Scale D to an integer factor for radius and spawn reduction.
        scale = int(D * constants.DOT_DISTANCE_SCALE)

        # Dot radius grows with distance (D) but is clamped to a maximum.
        self.dot_radius = min(constants.DOT_MAX_RADIUS, 1 + scale)

        # Difficulty level increases every DOT_DIFFICULTY_SCORE_STEP points.
        self.difficulty_level = score // constants.DOT_DIFFICULTY_SCORE_STEP

        # Base spawn interval reduced by difficulty level.
        base_interval = max(constants.DOT_MIN_BASE_INTERVAL,
                            constants.DOT_BASE_SPAWN_INTERVAL - self.difficulty_level * 2)
        # Reduction based on the complex constant distance D.
        reduction = int(D * constants.DOT_REDUCTION_MULTIPLIER)
        # Final spawn interval: clamped to a minimum.
        self.dot_spawn_interval = max(constants.DOT_MIN_SPAWN_INTERVAL, base_interval - reduction)

    def update_dots(self, score):
        """Spawns new dots and updates the position of existing dots.

        Args:
            score: The player's current score, used to check for spawn condition.
        """
        # Spawn new dot periodically once the player has reached the configured threshold.
        if score >= constants.SCORE_DOT_SPAWN_THRESHOLD and pyxel.frame_count % self.dot_spawn_interval == 0:
            speed = random.uniform(1.0, 3.0) # constant
            color = random.randint(2, 15)
            base_x = random.randint(0, self.WIDTH - 1)
            # Horizontal position oscillates slightly for visual variety.
            x = (base_x + math.sin(pyxel.frame_count * 0.1) * 20) % self.WIDTH
            # dot stored as [y, speed, color, sliced_flag, base_x, x]
            self.dots.append([0.0, speed, color, 0, base_x, x])

        # Update each dot's position and remove dots that have fallen off the screen.
        updated = []
        for y, speed, color, sliced, base_x, x in self.dots:
            # Sliced dots move faster for a brief visual effect.
            cur_speed = speed * (6 if sliced else 1)
            y += cur_speed
            # Recalculate horizontal oscillation for variety.
            x = (base_x + math.sin(pyxel.frame_count * 0.1) * 20) % self.WIDTH
            if y < self.HEIGHT:
                updated.append([y, speed, color, sliced, base_x, x])
        self.dots = updated

    def check_collision(self, head_x, head_y, size):
        """Checks for collision between the player's head and any unsliced dot.

        Args:
            head_x: The X coordinate of the player's head.
            head_y: The Y coordinate of the player's head.
            size: The size of the player's head segment.

        Returns:
            -1 if a collision occurred (and the dot is marked as sliced), 0 otherwise.
        """
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
            # Simple bounding box collision check: head segment vs dot circle.
            if (left < x + r and right > x - r and
                    top < y + r and bottom > y - r):
                # Mark the dot as sliced (hit).
                self.dots[i][3] = 1
                hit = True

        return -1 if hit else 0

    def draw(self):
        for y, speed, color, sliced, base_x, x in self.dots:
            # Draw dot as a circle.
            pyxel.circ(int(x), int(y), self.dot_radius, color)