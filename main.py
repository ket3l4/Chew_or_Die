"""The main application and game loop for the 'Chew or Die' game.

This module initializes the game, manages the state transitions between
menu, game, fractal mini-game, and lose screens, and handles the primary
update and draw loops.
"""

import pyxel
import random
import math
from typing import Tuple

import constants
from dot_manager import DotManager
from player import Player
from julia import Julia_set
import ui

class App:
    """The main class containing all the logic for the game."""
    def __init__(self):
        """Initializes the Pyxel screen and all game components."""
        pyxel.init(constants.APP_WIDTH, constants.APP_HEIGHT, title="Chew or Die", fps=constants.GAME_FPS)
        self.mode = constants.MENU_MODE
        self.is_sound_on = True
        self.selected_character = 1 # Placeholder for character selection logic.

        # Setup sound (a simple synth sequence).
        pyxel.sound(0).set("c2e2g2c3", "p", "6", "n", 5)
        # Initialize game objects.
        self.player = Player(constants.APP_WIDTH, constants.APP_HEIGHT, constants.SEGMENT_SIZE, constants.RAINBOW_COLORS)
        self.dot_manager = DotManager(constants.APP_WIDTH, constants.APP_HEIGHT)
        self.julia = Julia_set(constants.APP_WIDTH, constants.APP_HEIGHT, constants.GAME_FPS, self.dot_manager)

        self._reset_game_state()
        # Start the main Pyxel game loop.
        pyxel.run(self.update, self.draw)

    def _reset_game_state(self):
        """Resets all game-specific variables for a new game."""
        self.score = 5
        self.sliced_fx_timer = 0  # Timer for the '-1 SLICE!' text effect.

        # Re-initialize player and clear dots.
        self.player = Player(constants.APP_WIDTH, constants.APP_HEIGHT, constants.SEGMENT_SIZE, constants.RAINBOW_COLORS)
        self.dot_manager.dots = []

        # Setup the first fractal target C and spawn the first fruit.
        self.julia.reset_target_c(self.score)
        self.fruit_x, self.fruit_y = self.spawn_fruit(self.player.body)

    def spawn_fruit(self, forbidden: list[list[int]]) -> Tuple[int, int]:
        """Spawns fruit at a random grid location not occupied by the player's body.

        Args:
            forbidden: A list of [x, y] coordinates occupied by the player's body.

        Returns:
            A tuple (x, y) of the fruit's top-left grid coordinates.
        """
        # Calculate the actual pixel boundaries aligned to the segment grid.
        grid_w = constants.APP_WIDTH // constants.SEGMENT_SIZE * constants.SEGMENT_SIZE
        grid_h = constants.APP_HEIGHT // constants.SEGMENT_SIZE * constants.SEGMENT_SIZE

        # Loop until a safe, unoccupied position is found.
        while True:
            # Randomly select coordinates snapped to the grid (multiples of SEGMENT_SIZE).
            x = random.randrange(0, grid_w, constants.SEGMENT_SIZE)
            y = random.randrange(0, grid_h, constants.SEGMENT_SIZE)
            if [x, y] not in forbidden:
                return x, y

    def update(self):
        """The main update method, called every frame."""
        # Global quit key.
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        # Dispatch update logic based on the current game mode.
        if self.mode == constants.MENU_MODE:
            self.update_menu()
        elif self.mode == constants.GAME_MODE:
            self.update_game()
        elif self.mode == constants.FRACTAL_MODE:
            self.update_fractal()
        elif self.mode == constants.LOSE_MODE:
            # Allow returning to menu from the lose screen.
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.mode = constants.MENU_MODE

    def update_menu(self):
        """Handles input and logic for the main menu screen."""
        cx = constants.APP_WIDTH // 2
        start_y = constants.APP_HEIGHT // 2 - 70
        gap = 40
        bx = cx - constants.BUTTON_WIDTH // 2

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # Check for button clicks using a private helper.
            if self._btn_hover(bx, start_y):
                # PLAY button
                self._reset_game_state()
                self.mode = constants.GAME_MODE
            elif self._btn_hover(bx, start_y + gap):
                # SOUND button (currently unused in draw_menu)
                self.is_sound_on = not self.is_sound_on
            elif self._btn_hover(bx, start_y + gap * 2):
                # Placeholder for character select button (currently unused)
                self.selected_character = 1
            elif self._btn_hover(bx, start_y + gap * 3):
                # EXIT button
                pyxel.quit()

    def update_game(self):
        """Handles input and logic for the main snake gameplay loop."""
        # --- Player Movement Input ---
        # Only set direction on press (btnp) to prevent rapid changes.
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W):
            self.player.set_direction([0, -constants.SEGMENT_SIZE])
        elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S):
            self.player.set_direction([0, constants.SEGMENT_SIZE])
        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
            self.player.set_direction([-constants.SEGMENT_SIZE, 0])
        elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
            self.player.set_direction([constants.SEGMENT_SIZE, 0])

        self.dot_manager.update_dots(self.score)

        # Advance player movement.
        state, head = self.player.update_movement()
        if state == "COLLISION":
            self.mode = constants.LOSE_MODE
            return

        if state == "MOVE":
            head_x, head_y = head

            # --- Obstacle (Dots) Collision ---
            penalty = self.dot_manager.check_collision(head_x, head_y, constants.SEGMENT_SIZE)
            if penalty < 0:
                self.score += penalty
                self.sliced_fx_timer = 10  # Start visual effect timer.
                if self.is_sound_on:
                    pyxel.play(0, 0)

                if self.score <= 0:
                    self.mode = constants.LOSE_MODE
                    
            # --- Fruit Collision ---
            if head_x == self.fruit_x and head_y == self.fruit_y:
                # Enter the fractal mini-game (chewing phase).
                self.mode = constants.FRACTAL_MODE
                self.julia.start_timer()

    def update_fractal(self):
        """Handles input and logic for the chewing mini-game (FRACTAL_MODE)."""
        self.dot_manager.update_dots(self.score) # Dots continue to fall for increased difficulty.
        status = self.julia.update_chewing()

        if status == "LOSE":
            # Timer ran out in the fractal game.
            self.mode = constants.LOSE_MODE
        elif status == "WIN":
            # Successfully matched the target C.
            self.player.grow_body() # Grow the snake as a reward.
            self.score += 10 # Increase score.

            # Spawn new fruit and reset the fractal target C for the next round.
            self.fruit_x, self.fruit_y = self.spawn_fruit(self.player.body)
            self.julia.reset_target_c(self.score)
            self.mode = constants.GAME_MODE # Return to main gameplay.

    def _btn_hover(self, x, y):
        """Checks if the mouse is hovering over a button at (x, y).

        Args:
            x: The button's top-left X coordinate.
            y: The button's top-left Y coordinate.

        Returns:
            True if the mouse is hovering over the button, False otherwise.
        """
        return (x <= pyxel.mouse_x <= x + constants.BUTTON_WIDTH and
                y <= pyxel.mouse_y <= y + constants.BUTTON_HEIGHT)

    # --- Draw Delegators (for cleaner separation of concerns) ---

    def draw_fruit(self, x, y):
        """Delegates fruit drawing to the UI module."""
        ui.draw_fruit(x, y)


    def draw_button(self, x, y, text, base_color, hover_color):
        """Delegates button drawing to the UI module."""
        ui.draw_button(x, y, text, base_color, hover_color)


    def draw(self):
        """The main draw method, called every frame."""
        # Dispatch drawing logic based on the current game mode.
        if self.mode == constants.MENU_MODE:
            self.draw_menu()
        elif self.mode == constants.GAME_MODE:
            self.draw_game()
        elif self.mode == constants.FRACTAL_MODE:
            self.draw_fractal()
        elif self.mode == constants.LOSE_MODE:
            self.draw_lose()

    def draw_background(self):
        """Delegates background drawing to the UI module."""
        ui.draw_background(constants.APP_WIDTH, constants.APP_HEIGHT)

    def draw_menu(self):
        """Draws the main menu screen."""
        self.draw_background()
        pyxel.text(constants.APP_WIDTH // 2 - 40, 40, "CHEW OR DIE", 7) # Title

        cx = constants.APP_WIDTH // 2
        start_y = constants.APP_HEIGHT // 2 - 70
        gap = 40
        bx = cx - constants.BUTTON_WIDTH // 2

        # Draw buttons.
        self.draw_button(bx, start_y, "PLAY", 6, 12)
        # Note: The EXIT button is incorrectly drawn at gap*3 in update_menu but gap*1 here.
        # Following the `update_menu` logic's positions for consistency.
        self.draw_button(bx, start_y + gap, "SOUND: ON/OFF", 10, 5) # Placeholder for sound
        self.draw_button(bx, start_y + gap * 2, "CHARACTER", 14, 8) # Placeholder for character
        self.draw_button(bx, start_y + gap * 3, "EXIT", 11, 3)

        # Game description.
        pyxel.text(constants.APP_WIDTH // 2 - 170, 50, "SNAKE GAME but... WHEN YOU REACH THE FOOD YOU HAVE TO CHEW UNTIL YOU REACH THE TARGET", 7)

    def draw_game(self):
        """Draws the main gameplay screen."""
        self.draw_background()

        self.dot_manager.draw()
        self.draw_fruit(self.fruit_x, self.fruit_y)

        self.player.draw(self.selected_character)

        # Draw score and difficulty overlay.
        pyxel.text(4, 4, f"SCORE: {self.score}", 7)
        # Display a numerical representation of the current dot danger level.
        danger_level = int(self.dot_manager.dot_radius * self.dot_manager.dot_spawn_interval / 10)
        pyxel.text(4, constants.APP_HEIGHT - 10,
                   f"DANGER LEVEL = {danger_level}",
                   10)

        # Draw the sliced/penalty effect text.
        if self.sliced_fx_timer > 0:
            pyxel.text(constants.APP_WIDTH // 2 - 30, 20, "-1 SLICE!", 8)
            self.sliced_fx_timer -= 1

    def draw_fractal(self):
        """Draws the chewing mini-game (FRACTAL_MODE) screen."""
        self.draw_background()
        self.dot_manager.draw() # Still draw dots in the background.
        self.julia.draw_fractal()

    def draw_lose(self):
        """Draws the game over (LOSE_MODE) screen."""
        self.draw_background()
        pyxel.text(constants.APP_WIDTH // 2 - 30, constants.APP_HEIGHT // 2 - 20,
                   "STOMACH ACHE!", 7)
        pyxel.text(constants.APP_WIDTH // 2 - 40, constants.APP_HEIGHT // 2,
                   f"FINAL SCORE: {self.score}", 7)
        pyxel.text(constants.APP_WIDTH // 2 - 90, constants.APP_HEIGHT // 2 + 20,
                   "PRESS SPACE TO RETURN", 7)

# Start the application.
App()
