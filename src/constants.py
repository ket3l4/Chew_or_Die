# --- Pixel Constants ---
APP_WIDTH = 512  # Pyxel screen width in pixels.
APP_HEIGHT = 384  # Pyxel screen height in pixels.
GAME_FPS = 30  # Game frames per second.
SEGMENT_SIZE = 16  # Size of one snake/player segment in pixels.

# --- Game Modes ---
MENU_MODE = 0  # Main menu state.
GAME_MODE = 1  # Standard snake gameplay state.
FRACTAL_MODE = 2  # Chewing mini-game (Julia set) state.
LOSE_MODE = 3  # Game over state.

# --- Fractal (Julia Set) Constants ---
MAX_ITER = 40  # Maximum number of iterations for the Julia set calculation.
BASE_C_REAL = -0.5  # Baseline real component for the complex constant c.
BASE_C_IMAG = 0.0  # Baseline imaginary component for the complex constant c.
DIFFICULTY_BASELINE_C = complex(BASE_C_REAL, BASE_C_IMAG)  # The base complex constant for difficulty scaling.
WINNING_TOLERANCE = 0.015  # Maximum distance between current C and target C to win the chewing game.
CHEWING_TIME_SECONDS = 10  # Duration of the chewing mini-game in seconds.

# Julia set bounds for mapping pixels to the complex plane (Z-plane)
FRACTAL_MIN_X = -1.5
FRACTAL_MAX_X = 1.5
FRACTAL_MIN_Y = -1.5
FRACTAL_MAX_Y = 1.5

# --- Penalties ---
# Points subtracted when the chewing mini-game times out (use positive integer)
FRACTAL_TIMEOUT_PENALTY = 4

# --- UI Constants ---
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
RAINBOW_COLORS = [2, 6, 12, 11, 10, 14, 2]  # Colors used for the snake's body segments.

BACKGROUND_COLORS = [2, 14, 10, 11, 12, 6, 2]  # Colors used to draw the background gradient.
BACKGROUND_BAND_HEIGHT = 6  # Height of each color band in the background gradient.

# --- Gameplay tuning ---
INITIAL_SCORE = 5  # Starting player score
PLAYER_MOVE_SPEED = 10  # Frames per movement for the player
PLAYER_SPEED_DECREASE_PER_LEVEL = 1  # How many frames to reduce per difficulty level
PLAYER_MIN_MOVE_SPEED = 1  # Minimum frames per movement (fastest)

# --- Dot (obstacle) tuning ---
DOT_INITIAL_RADIUS = 4
DOT_BASE_SPAWN_INTERVAL = 16
DOT_MIN_BASE_INTERVAL = 6
DOT_MIN_SPAWN_INTERVAL = 2
DOT_DISTANCE_SCALE = 10
DOT_REDUCTION_MULTIPLIER = 25
DOT_MAX_RADIUS = 20
SCORE_DOT_SPAWN_THRESHOLD = 10

# Spawn difficulty scaling: every N points difficulty level increases
DOT_DIFFICULTY_SCORE_STEP = 15

# --- UI / Timing ---
MENU_BUTTON_GAP = 40
SLICED_FX_DURATION = 15  # Frames to display '-1 SLICE!'
STOMACHACHE_DURATION = GAME_FPS  # Frames to display stomachache penalty (1 second)

# --- Julia rendering tuning ---
JULIA_RENDER_STEP = 2  # Render at 2x2 pixel blocks for performance
PALETTE_WRAP = 14
PALETTE_OFFSET = 2
CHEW_TIMER_DECREMENT = 2
