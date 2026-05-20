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

# --- THEME MODERNE (Sleek Dark Mode) ---
# Fond et panneaux
C_BG        = (15, 23, 42)      # Bleu nuit très profond (Slate 900)
C_PANEL     = (30, 41, 59)      # Panneaux flottants (Slate 800)
C_BORDER    = (51, 65, 85)      # Bordures subtiles (Slate 700)

# Textes et Accents
C_WHITE     = (248, 250, 252)   # Blanc cassé très doux pour la lecture
C_GREY      = (148, 163, 184)   # Gris moderne pour les textes secondaires ou indices
C_GOLD      = (34, 211, 238)    # Accent : Cyan néon/vibrant 

# Feedbacks
C_SUCCESS   = (34, 197, 94)     # Vert pastel (Validation)
C_FAIL      = (239, 68, 68)     # Rouge moderne (Erreur)

# Boutons
C_BTN       = (79, 70, 229)     # Indigo vif (Couleur primaire UI)
C_BTN_HOVER = (99, 102, 241)    # Indigo plus clair au survol
C_BTN_TEXT  = (255, 255, 255)   # Texte des boutons (Blanc pur)

# --- CONSTANTES VISUELLES D'ARRIÈRE-PLAN ---
# (Adaptées au nouveau thème sombre pour rester esthétiques)
C_NOTE_FILL = (34, 211, 238)    # Notes de musique en Cyan (rappel de l'accent)
C_NOTE_LINE = (15, 23, 42)      # Contours de la portée fusionnés avec le fond
C_DOT_GRID  = (25, 33, 50)      # Grille de points à peine visible pour donner de la texture