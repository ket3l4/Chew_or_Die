
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
    """
    The main class containing all the logic for the game.
    """
    def __init__(self):
        """

        """
        pyxel.init(constants.APP_WIDTH, constants.APP_HEIGHT, title="Chew or Die", fps=constants.GAME_FPS)
        self.mode = constants.MENU_MODE
        self.is_sound_on = True
        self.selected_character = 1

        pyxel.sound(0).set("c2e2g2c3", "p", "6", "n", 5)
        self.player = Player(constants.APP_WIDTH, constants.APP_HEIGHT, constants.SEGMENT_SIZE, constants.RAINBOW_COLORS)
        self.dot_manager = DotManager(constants.APP_WIDTH, constants.APP_HEIGHT)
        self.julia = Julia_set(constants.APP_WIDTH, constants.APP_HEIGHT, constants.GAME_FPS, self.dot_manager)

        self._reset_game_state()
        pyxel.run(self.update, self.draw)

    def _reset_game_state(self):
        self.score = 5
        self.sliced_fx_timer = 0

        self.player = Player(constants.APP_WIDTH, constants.APP_HEIGHT, constants.SEGMENT_SIZE, constants.RAINBOW_COLORS)
        self.dot_manager.dots = []

        self.julia.reset_target_c(self.score)
        self.fruit_x, self.fruit_y = self.spawn_fruit(self.player.body)

    def spawn_fruit(self, forbidden):
        grid_w = constants.APP_WIDTH // constants.SEGMENT_SIZE * constants.SEGMENT_SIZE
        grid_h = constants.APP_HEIGHT // constants.SEGMENT_SIZE * constants.SEGMENT_SIZE

        while True:
            x = random.randrange(0, grid_w, constants.SEGMENT_SIZE)
            y = random.randrange(0, grid_h, constants.SEGMENT_SIZE)
            if [x, y] not in forbidden:
                return x, y
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if self.mode == constants.MENU_MODE:
            self.update_menu()
        elif self.mode == constants.GAME_MODE:
            self.update_game()
        elif self.mode == constants.FRACTAL_MODE:
            self.update_fractal()
        elif self.mode == constants.LOSE_MODE:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.mode = constants.MENU_MODE

    def update_menu(self):
        cx = constants.APP_WIDTH // 2
        start_y = constants.APP_HEIGHT // 2 - 70
        gap = 40
        bx = cx - constants.BUTTON_WIDTH // 2

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self._btn_hover(bx, start_y):
                self._reset_game_state()
                self.mode = constants.GAME_MODE
            elif self._btn_hover(bx, start_y + gap):
                self.is_sound_on = not self.is_sound_on
            elif self._btn_hover(bx, start_y + gap * 2):
                self.selected_character = 1
            elif self._btn_hover(bx, start_y + gap * 3):
                pyxel.quit()

    def update_game(self):
        # --- Input
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W):
            self.player.set_direction([0, -constants.SEGMENT_SIZE])
        elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S):
            self.player.set_direction([0, constants.SEGMENT_SIZE])
        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
            self.player.set_direction([-constants.SEGMENT_SIZE, 0])
        elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
            self.player.set_direction([constants.SEGMENT_SIZE, 0])


        self.dot_manager.update_dots(self.score)

        # Advance player movement
        state, head = self.player.update_movement()
        if state == "COLLISION":
            self.mode = constants.LOSE_MODE
            return

        if state == "MOVE":
            head_x, head_y = head

            # dots collision
            penalty = self.dot_manager.check_collision(head_x, head_y, constants.SEGMENT_SIZE)
            if penalty < 0:
                self.score += penalty
                self.sliced_fx_timer = 10
                if self.is_sound_on:
                    pyxel.play(0, 0)

                if self.score <= 0:
                    self.mode = constants.LOSE_MODE
                    
            # Fruit collision
            if head_x == self.fruit_x and head_y == self.fruit_y:
                self.mode = constants.FRACTAL_MODE
                self.julia.start_timer()

    def update_fractal(self):
        self.dot_manager.update_dots(self.score)
        status = self.julia.update_chewing()

        if status == "LOSE":
            self.mode = constants.LOSE_MODE
        elif status == "WIN":
            self.player.grow_body()
            self.score += 10

            self.fruit_x, self.fruit_y = self.spawn_fruit(self.player.body)
            self.julia.reset_target_c(self.score)
            self.mode = constants.GAME_MODE

    def _btn_hover(self, x, y):
        return (x <= pyxel.mouse_x <= x + constants.BUTTON_WIDTH and
                y <= pyxel.mouse_y <= y + constants.BUTTON_HEIGHT)

    def draw_fruit(self, x, y):
        # delegate to ui library
        ui.draw_fruit(x, y)


    def draw_button(self, x, y, text, base_color, hover_color):
        ui.draw_button(x, y, text, base_color, hover_color)


    def draw(self):
        if self.mode == constants.MENU_MODE:
            self.draw_menu()
        elif self.mode == constants.GAME_MODE:
            self.draw_game()
        elif self.mode == constants.FRACTAL_MODE:
            self.draw_fractal()
        elif self.mode == constants.LOSE_MODE:
            self.draw_lose()

    def draw_background(self):
        ui.draw_background(constants.APP_WIDTH, constants.APP_HEIGHT)

    def draw_menu(self):
        self.draw_background()
        pyxel.text(constants.APP_WIDTH // 2 - 40, 40, "CHEW OR DIE", 7)

        cx = constants.APP_WIDTH // 2
        start_y = constants.APP_HEIGHT // 2 - 70
        gap = 40
        bx = cx - constants.BUTTON_WIDTH // 2

        self.draw_button(bx, start_y, "PLAY", 6, 12)
        self.draw_button(bx, start_y + gap, "EXIT", 11, 3)
        pyxel.text(constants.APP_WIDTH // 2 - 170, 50, "SNAKE GAME but... WHEN YOU REACH THE FOOD YOU HAVE TO CHEW UNTIL YOU REACH THE TARGET", 7)

    def draw_game(self):
        self.draw_background()

        self.dot_manager.draw()
        self.draw_fruit(self.fruit_x, self.fruit_y)

        self.player.draw(self.selected_character)

        pyxel.text(4, 4, f"SCORE: {self.score}", 7)
        pyxel.text(4, constants.APP_HEIGHT - 10,
                   f"DANGER LEVEL = {int(self.dot_manager.dot_radius * self.dot_manager.dot_spawn_interval / 10)}",
                   10)

        if self.sliced_fx_timer > 0:
            pyxel.text(constants.APP_WIDTH // 2 - 30, 20, "-1 SLICE!", 8)
            self.sliced_fx_timer -= 1

    def draw_fractal(self):
        self.draw_background()
        self.dot_manager.draw()
        self.julia.draw_fractal()

    def draw_lose(self):
        self.draw_background()
        pyxel.text(constants.APP_WIDTH // 2 - 30, constants.APP_HEIGHT // 2 - 20,
                   "STOMACH ACHE!", 7)
        pyxel.text(constants.APP_WIDTH // 2 - 40, constants.APP_HEIGHT // 2,
                   f"FINAL SCORE: {self.score}", 7)
        pyxel.text(constants.APP_WIDTH // 2 - 90, constants.APP_HEIGHT // 2 + 20,
                   "PRESS SPACE TO RETURN", 7)

App()
