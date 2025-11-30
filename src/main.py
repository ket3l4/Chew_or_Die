import pyxel
import random
import math

from constants import *
from dot_manager import DotManager
from player import Player
from julia import Julia_set

class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Chew or Die", fps=FPS)

        self.mode = MENU_MODE
        self.is_sound_on = True
        self.selected_character = 1

        pyxel.sound(0).set("c2e2g2c3", "p", "6", "n", 5)

        self.player = Player(WIDTH, HEIGHT, SEGMENT_SIZE, RAINBOW_COLORS)
        self.dot_manager = DotManager(WIDTH, HEIGHT)
        self.julia = Julia_set(WIDTH, HEIGHT, FPS, self.dot_manager)

        self._reset_game_state()
        pyxel.run(self.update, self.draw)

    def _reset_game_state(self):
        self.score = 5
        self.sliced_fx_timer = 0

        self.player = Player(WIDTH, HEIGHT, SEGMENT_SIZE, RAINBOW_COLORS)
        self.dot_manager.dots = []

        self.julia.reset_target_c(self.score)
        self.fruit_x, self.fruit_y = self.spawn_fruit(self.player.body)

    def spawn_fruit(self, forbidden):
        grid_w = WIDTH // SEGMENT_SIZE * SEGMENT_SIZE
        grid_h = HEIGHT // SEGMENT_SIZE * SEGMENT_SIZE

        while True:
            x = random.randrange(0, grid_w, SEGMENT_SIZE)
            y = random.randrange(0, grid_h, SEGMENT_SIZE)
            if [x, y] not in forbidden:
                return x, y

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.mode == MENU_MODE:
            self.update_menu()
        elif self.mode == GAME_MODE:
            self.update_game()
        elif self.mode == FRACTAL_MODE:
            self.update_fractal()
        elif self.mode == LOSE_MODE:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.mode = MENU_MODE

    def update_menu(self):
        cx = WIDTH // 2
        start_y = HEIGHT // 2 - 70
        gap = 40
        bx = cx - BUTTON_W // 2

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self._btn_hover(bx, start_y):
                self._reset_game_state()
                self.mode = GAME_MODE
            elif self._btn_hover(bx, start_y + gap):
                self.is_sound_on = not self.is_sound_on
            elif self._btn_hover(bx, start_y + gap * 2):
                self.selected_character = 1
            elif self._btn_hover(bx, start_y + gap * 3):
                pyxel.quit()

    def update_game(self):
        # --- Input
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W):
            self.player.set_direction([0, -SEGMENT_SIZE])
        elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S):
            self.player.set_direction([0, SEGMENT_SIZE])
        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
            self.player.set_direction([-SEGMENT_SIZE, 0])
        elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
            self.player.set_direction([SEGMENT_SIZE, 0])


        self.dot_manager.update_dots(self.score)

        state, head = self.player.update_movement()
        if state == "COLLISION":
            self.mode = LOSE_MODE
            return

        if state == "MOVE":
            hx,hy = head

            # dots colision
            penalty = self.dot_manager.check_collision(hx, hy, SEGMENT_SIZE)
            if penalty < 0:
                self.score += penalty
                self.sliced_fx_timer = 10
                if self.is_sound_on:
                    pyxel.play(0, 0)

                if self.score <= 0:
                    self.mode = LOSE_MODE
                    
            #Fruit collision
            if hx == self.fruit_x and hy == self.fruit_y:
                self.mode = FRACTAL_MODE
                self.julia.start_timer()

    def update_fractal(self):
        self.dot_manager.update_dots(self.score)
        status = self.julia.update_chewing()

        if status == "LOSE":
            self.mode = LOSE_MODE
        elif status == "WIN":
            self.player.grow_body()
            self.score += 10

            self.fruit_x, self.fruit_y = self.spawn_fruit(self.player.body)
            self.julia.reset_target_c(self.score)
            self.mode = GAME_MODE

    def _btn_hover(self, x, y):
        return (x <= pyxel.mouse_x <= x + BUTTON_W and
                y <= pyxel.mouse_y <= y + BUTTON_H)

    def draw_fruit(self, x, y):
        # red apple
        pyxel.circ(x + 8, y + 8, 6, 8)
        # highlight
        pyxel.circ(x + 5, y + 5, 2, 7)
        # stem
        pyxel.rect(x + 7, y + 1, 2, 3, 4)


    def draw_button(self, x, y, text, base_color, hover_color):
        hover = self._btn_hover(x, y)
        color = hover_color if hover else base_color
        pyxel.rect(x, y, BUTTON_W, BUTTON_H, color)

        text_x = x + (BUTTON_W - len(text) * 4) // 2
        text_y = y + (BUTTON_H - 6) // 2
        pyxel.text(text_x, text_y, text, 0)


    def draw(self):
        if self.mode == MENU_MODE:
            self.draw_menu()
        elif self.mode == GAME_MODE:
            self.draw_game()
        elif self.mode == FRACTAL_MODE:
            self.draw_fractal()
        elif self.mode == LOSE_MODE:
            self.draw_lose()

    def draw_menu(self):
        pyxel.cls(1)
        pyxel.text(WIDTH // 2 - 40, 40, "CHEW OR DIE", 7)

        cx = WIDTH // 2
        start_y = HEIGHT // 2 - 70
        gap = 40
        bx = cx - BUTTON_W // 2

        self.draw_button(bx, start_y, "PLAY", 3, 11)
        self.draw_button(bx, start_y + gap, "EXIT", 9, 2)

    def draw_game(self):
        pyxel.cls(1)

        self.dot_manager.draw()
        self.draw_fruit(self.fruit_x, self.fruit_y)

        self.player.draw(self.selected_character)

        pyxel.text(4, 4, f"SCORE: {self.score}", 7)
        pyxel.text(4, HEIGHT - 10,
                   f"DANGER LEVEL = {int(self.dot_manager.dot_radius * self.dot_manager.dot_spawn_interval / 10)}",
                   10)

        if self.sliced_fx_timer > 0:
            pyxel.text(WIDTH // 2 - 30, 20, "-1 SLICE!", 8)
            self.sliced_fx_timer -= 1

    def draw_fractal(self):
        self.dot_manager.draw()
        self.julia.draw_fractal()

    def draw_lose(self):
        pyxel.cls(9)
        pyxel.text(WIDTH // 2 - 30, HEIGHT // 2 - 20,
                   "STOMACH ACHE!", 7)
        pyxel.text(WIDTH // 2 - 40, HEIGHT // 2,
                   f"FINAL SCORE: {self.score}", 7)
        pyxel.text(WIDTH // 2 - 90, HEIGHT // 2 + 20,
                   "PRESS SPACE TO RETURN", 7)

App()
