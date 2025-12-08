# Chew or Die - Copilot Instructions

## Project Overview
**Chew or Die** is a Pyxel-based retro arcade game combining snake mechanics with a Julia set fractal mini-game. The player controls a snake, eats fruit to trigger chewing challenges (where they navigate a complex plane to match a target Julia constant), and avoids falling obstacle dots. Difficulty scales with score and fractal proximity.

## Architecture: State Machine Pattern
The game uses four distinct modes controlled via `constants` integer flags:
- `MENU_MODE` (0): Main menu with clickable buttons
- `GAME_MODE` (1): Snake gameplay with obstacle spawning
- `FRACTAL_MODE` (2): Julia set mini-game (complex number navigation)
- `LOSE_MODE` (3): Game over screen

**Key controller**: `App` class in `main.py` dispatches `update()` and `draw()` calls based on mode.

## Critical Components & Data Structures

### Player (Snake)
- **File**: `player.py`
- **Data**: `body` is a list of `[x, y]` segments; index 0 is head
- **Movement**: Grid-aligned to `SEGMENT_SIZE` (16 pixels); wraps screen edges
- **Growth**: Call `grow_body()` to add tail segment (skip pop in `update_movement()`)
- **Prevention**: `set_direction()` blocks 180° reversals to avoid instant death

### DotManager (Obstacles)
- **File**: `dot_manager.py`
- **Data format**: `[y, speed, color, sliced_flag, base_x, x]`
- **Spawning**: Only if score ≥ 10, every `dot_spawn_interval` frames
- **Difficulty scaling**: `difficulty(score, target_c_real, target_c_imag)` adjusts spawn rate and radius based on Julia set distance
- **Collision**: AABB check with `dot_radius` margin

### Julia Set Mini-Game
- **File**: `julia.py`
- **Target**: Random complex number near `BASE_C` (±0.15 offset in real/imaginary)
- **Win condition**: Player's C value within `WINNING_TOLERANCE` (0.02) distance
- **Iteration**: Standard formula `z = z*z + c` up to `MAX_ITER` (40)
- **Performance**: Rendered at 2x2 pixel step to reduce lag
- **Timing**: `CHEWING_TIME_SECONDS` (10s) countdown; exceed limit = lose

### UI Helpers
- **File**: `ui.py`
- **Functions**: `draw_background()` (gradient bands), `draw_button()` (hover-aware)
- **Button pattern**: Position at `(x, y)`, check `pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)` in `update_menu()`

## Development Patterns & Key Files

### Update-Draw Separation
- **Never render in `update()` methods** — all drawing in `draw()` methods
- `update()` changes state; `draw()` visualizes it
- Example: `dot_manager.update_dots()` spawns/moves, `dot_manager.draw()` renders

### Frame-Based Timing
- Use `pyxel.frame_count % interval == 0` for spawning/events (see `dot_manager.update_dots()`)
- Use timers for countdowns: `chew_timer -= 1` in `update_fractal()`
- Debounce input: `input_delay` counter prevents rapid key repeats

### Collision Detection Patterns
- **Dot collision (AABB)**: Check distance between head and dot center ≤ `dot_radius + SEGMENT_SIZE/2`
- **Self-collision**: Check if new head `[nx, ny]` in `body[:-1]` (exclude tail being vacated)
- **Fruit collision (grid)**: `head_x == fruit_x and head_y == fruit_y` (exact grid match)
- **Fractal win**: `distance(c_fixed, target_c) < WINNING_TOLERANCE`

### Input Handling
- **Game mode**: `pyxel.btnp(pyxel.KEY_*)` detects single press; prevents direction queue
- **Menu**: `pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)` + helper `_btn_hover()` checks bounds
- **Global quit**: `pyxel.btnp(pyxel.KEY_Q)` callable from any mode

## Game Balance Tuning Points

| Aspect | File | Key Variables |
|--------|------|----------------|
| Fractal difficulty | `constants.py`, `julia.py` | `CHEWING_TIME_SECONDS` (10s), `WINNING_TOLERANCE` (0.02) |
| Dot spawn rate | `dot_manager.py` | `dot_spawn_interval` formula, score threshold `>= 10` |
| Difficulty progression | `dot_manager.py` | `difficulty_level = score // 30`, `BASE_C_REAL`, distance scaling |
| Snake speed | `player.py` | `move_speed = 5` frames per segment |
| Initial score | `main.py` | `score = 5` in `_reset_game_state()` |

## Running & Testing
```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install pyxel

# Run
python main.py    # or: python3 main.py
```

**Debug tips**: 
- Print `pyxel.frame_count` to diagnose timing issues
- Use `print(self.player.body)` to debug snake state
- Check `julia_iter()` output for fractal rendering correctness

## Known Quirks
- **Fractal rendering lag**: 2x2 pixel step is an intentional performance trade-off (see comment in `julia.py`)
- **Dot oscillation**: Horizontal sway uses `sin(pyxel.frame_count * 0.1)` for visual variety
- **Palette limits**: Pyxel supports only 16 colors (0-15); color wrapping uses modulo

## Module Dependencies
- **pyxel**: Game engine (2.5.10+), handles rendering, input, audio
- **No external game libraries**: All physics/collision custom-implemented
- **Python 3.13+**: Required per `pyproject.toml`
