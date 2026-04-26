"""
NeuroBeat — Global constants.
Change values here to tune the whole game without touching logic files.
"""

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

# ── Colour palette ──────────────────────────────────────────────────────────
# Matches the royal-blue + gold theme from the PDF mockups
C_BG        = ( 35,  38, 158)   # Deep royal blue
C_PANEL     = ( 18,  20,  90)   # Dark navy card
C_BORDER    = (200, 165,  35)   # Gold border
C_GOLD      = (255, 210,  50)   # Gold accents / note heads
C_WHITE     = (255, 255, 255)
C_GREY      = (170, 175, 220)
C_SUCCESS   = ( 50, 220, 100)
C_FAIL      = (255,  70,  70)
C_BTN       = ( 55,  85, 215)   # Blue button
C_BTN_HOVER = ( 80, 120, 255)
C_NOTE_FILL = (255, 210,  50)   # Musical note head fill
C_NOTE_LINE = ( 10,  10,  50)   # Musical note outline / staff lines
C_DOT_GRID  = ( 48,  52, 175)   # Subtle background dot-grid
