"""The main application and game loop for the 'Chew or Die' game.

This module initializes the game, manages the state transitions between
menu, game, fractal mini-game, and lose screens, and handles the primary
update and draw loops.
"""

import pyxel
import random
from typing import Tuple

import constants
import ui
from dot_manager import DotManager
from player import Player
from julia import Julia_set

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

        # Setup for loading and displaying highscores.
        self.highscores = {}
        self.show_highscores = False

        self._reset_game_state()
        # Read highscores from highscore.txt
        self.load_highscores()
        # Start the main Pyxel game loop.
        pyxel.run(self.update, self.draw)

    def _reset_game_state(self):
        """Resets all game-specific variables for a new game."""
        self.score = constants.INITIAL_SCORE
        self.sliced_fx_timer = 0  # Timer for the '-1 SLICE!' text effect.
        self.stomachache_timer = 0  # Timer for the 'STOMACH ACHE! -4' penalty text.

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

    def save_score(self):
        """Append the current score to the highscore file."""
        try:
            with open("highscore.txt", "a") as f:
                f.write(str(self.score) + "\n")
        except Exception:
            # If something goes wrong, just ignore it.
            pass

    def load_highscores(self):
        """
        Load scores from the file and store them in a dict:
        {1: highest_score, 2: next_highest, ...}
        """
        scores = []
        try:
            with open("highscore.txt", "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            value = int(line)
                            scores.append(value)
                        except ValueError:
                            # Ignore malformed lines.
                            continue
        except FileNotFoundError:
            self.highscores = {}
            return

        # Sort descending so key 1 is the best score.
        scores.sort(reverse=True)
        # Use dictionary comprehension to update instance attribute.
        self.highscores = {i + 1: score for i, score in enumerate(scores)}

    def handle_game_over(self):
        """Store the score, refresh highscores, and switch to lose screen.
        Encompasses several methods - necessary after adding the highscore function."""
        self.save_score()
        self.load_highscores()
        self.mode = constants.LOSE_MODE

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
        gap = constants.MENU_BUTTON_GAP
        bx = cx - constants.BUTTON_WIDTH // 2

        # If we are currently looking at the HIGHSCORERS "screen":
        if self.show_highscores:
            # SPACE returns to the normal menu.
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.show_highscores = False
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # Check for button clicks using a private helper.
            if self._btn_hover(bx, start_y):
                # PLAY button
                self._reset_game_state()
                self.mode = constants.GAME_MODE
            elif self._btn_hover(bx, start_y + gap):
                # Toggle the highscore panel; always pressable
                self.show_highscores = True
                self.load_highscores()
            elif self._btn_hover(bx, start_y + gap * 2):
                # EXIT button
                pyxel.quit()
            elif self._btn_hover(bx, start_y + gap * 3 ):
                # SOUND button (currently unused in draw_menu)
                self.is_sound_on = not self.is_sound_on
            elif self._btn_hover(bx, start_y + gap * 4):
                # Placeholder for character select button (currently unused)
                self.selected_character = 1

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

        # Adjust player speed based on current difficulty level (lower move_speed = faster)
        new_speed = max(
            constants.PLAYER_MIN_MOVE_SPEED,
            constants.PLAYER_MOVE_SPEED - self.dot_manager.difficulty_level * constants.PLAYER_SPEED_DECREASE_PER_LEVEL,
        )
        self.player.move_speed = new_speed

        # Advance player movement.
        state, head = self.player.update_movement()
        if state == "COLLISION":
            self.handle_game_over()
            return

        if state == "MOVE":
            head_x, head_y = head

            # --- Obstacle (Dots) Collision ---
            penalty = self.dot_manager.check_collision(head_x, head_y, constants.SEGMENT_SIZE)
            if penalty < 0:
                self.score += penalty
                self.sliced_fx_timer = constants.SLICED_FX_DURATION  # Start visual effect timer.
                if self.is_sound_on:
                    pyxel.play(0, 0)

                if self.score <= 0:
                    self.handle_game_over()
                    
            # --- Fruit Collision ---
            if head_x == self.fruit_x and head_y == self.fruit_y:
                # Enter the fractal mini-game (chewing phase).
                self.mode = constants.FRACTAL_MODE
                self.julia.start_timer()

    def update_fractal(self):
        """Handles input and logic for the chewing mini-game (FRACTAL_MODE)."""
        self.dot_manager.update_dots(self.score) # Dots continue to fall for increased difficulty.
        status = self.julia.update_chewing()
        if status == "LOSE" or status == "TIMEOUT":
            # Timer ran out in the fractal game. Penalize the player by the configured constant.
            self.score -= constants.FRACTAL_TIMEOUT_PENALTY
            # If score falls to zero or below, go to the lose screen.
            if self.score <= 0:
                self.handle_game_over()
                return
            # Show a short "stomachache" penalty text when timing out.
            self.stomachache_timer = constants.STOMACHACHE_DURATION
            # Otherwise, reset fractal target and respawn fruit, return to game.
            self.fruit_x, self.fruit_y = self.spawn_fruit(self.player.body)
            self.julia.reset_target_c(self.score)
            self.mode = constants.GAME_MODE
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
        self.draw_button(bx, start_y + gap, "HIGHSCORE", 13, 10)
        self.draw_button(bx, start_y + gap * 2, "EXIT", 11, 3)

        # Highscore panel (always available, but only shown when toggled on).
        if self.show_highscores:
            self.draw_highscores()
        else:
            # Normal description only when not in highscore screen.
            pyxel.text(
                constants.APP_WIDTH // 2 - 170,
                50,
                "SNAKE GAME with CHEWING MINI-GAME (uses Julia Set Fractal simulator)",
                7,
            )

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
                   7)

        # Draw the sliced/penalty effect text.
        if self.sliced_fx_timer > 0:
            pyxel.text(constants.APP_WIDTH // 2 - 30, 20, "-1 SLICE!", 8)
            self.sliced_fx_timer -= 1
        # Draw the stomachache penalty when applicable.
        if getattr(self, 'stomachache_timer', 0) > 0:
            pyxel.text(constants.APP_WIDTH // 2 - 48, 32, f"STOMACH ACHE! -{constants.FRACTAL_TIMEOUT_PENALTY}", 8)
            self.stomachache_timer -= 1

    def draw_fractal(self):
        """Draws the chewing mini-game (FRACTAL_MODE) screen."""
        self.draw_background()
        self.dot_manager.draw() # Still draw dots in the background.
        self.julia.draw_fractal()
    def draw_highscores(self):
        """Draw the highscores 'screen' on top of the menu."""
        # Fill the whole screen with a solid color to hide menu buttons.
        pyxel.rect(0, 0, constants.APP_WIDTH, constants.APP_HEIGHT, 13)

        left = 20
        top = 30

        pyxel.text(left, top, "HIGHSCORES", 7)

        if not self.highscores:
            pyxel.text(left, top + 12, "No highscores yet ):", 7)
        else:
            max_entries = 10
            for rank in range(1, min(len(self.highscores), max_entries) + 1):
                score = self.highscores.get(rank, 0)
                pyxel.text(left, top + 12 + rank * 10, f"{rank}. {score}", 7)

        pyxel.text(left, top + 140, "PRESS SPACE TO RETURN", 7)



    def draw_lose(self):
        """Draws the game over (LOSE_MODE) screen."""
        self.draw_background()
        pyxel.text(constants.APP_WIDTH // 2 - 30, constants.APP_HEIGHT // 2 - 20,
                   "STOMACH ACHE! X w X", 1)
        pyxel.text(constants.APP_WIDTH // 2 - 30, constants.APP_HEIGHT // 2,
                   f"SCORE: {self.score}", 1)
        pyxel.text(constants.APP_WIDTH // 2 - 30, constants.APP_HEIGHT // 2 + 20,
                   "PRESS SPACE TO RETURN", 1)

# Start the application.
App()