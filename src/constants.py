# constants.py
"""
NeuroBeat — Global constants.
Change values here to tune the whole game without touching logic files.
"""
import pygame

# Window
WIDTH  = 1280
HEIGHT = 720
FPS    = 60

# Screen durations (seconds)
SPLASH_DURATION  = 3.5
PLAY_DURATION    = 30.0
LISTEN_DURATION  = 10.0
JUDGE_DELAY      = 2.0
MAX_ROUNDS       = 10

# --- MODERN THEME (Sleek Dark Mode) ---
# Background and panels
C_BG        = (15, 23, 42)      # Very deep midnight blue (Slate 900)
C_PANEL     = (30, 41, 59)      # Floating panels (Slate 800)
C_BORDER    = (51, 65, 85)      # Subtle borders (Slate 700)

# Texts and Accents
C_WHITE     = (248, 250, 252)   # Very soft off-white for reading
C_GREY      = (148, 163, 184)   # Modern grey for secondary texts or hints
C_GOLD      = (34, 211, 238)    # Accent: Neon/vibrant Cyan 

# Feedbacks
C_SUCCESS   = (34, 197, 94)     # Pastel green (Validation)
C_FAIL      = (239, 68, 68)     # Modern red (Error)

# Buttons
C_BTN       = (79, 70, 229)     # Bright indigo (Primary UI color)
C_BTN_HOVER = (99, 102, 241)    # Lighter indigo on hover
C_BTN_TEXT  = (255, 255, 255)   # Button text (Pure white)

# --- VISUAL BACKGROUND CONSTANTS ---
# (Adapted to the new dark theme to remain aesthetic)
C_NOTE_FILL = (34, 211, 238)    # Music notes in Cyan (accent reminder)
C_NOTE_LINE = (15, 23, 42)      # Staff outlines merged with the background
C_DOT_GRID  = (25, 33, 50)      # Barely visible dot grid to provide texture