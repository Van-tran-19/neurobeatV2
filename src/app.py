# app.py
"""
NeuroBeat — Application controller.

Owns the pygame window, the clock, the database instance, the GameEngine,
and the screen registry. All screen navigation goes through `app.go_to(key)`.
"""
from __future__ import annotations

import sys
import os
import pygame
from src.constants import WIDTH, HEIGHT, FPS
from data.database import DatabaseManager
from src.game_logic import GameEngine
from src.screens.splash_screen import SplashScreen
from src.screens.home_screen import HomeScreen
from src.screens.game_screen import GameScreen
from src.screens.login_screen import LoginScreen
from src.screens.leaderboard_screen import LeaderboardScreen
from src.screens.stats_screen import StatsScreen
AUDIO_PATH = os.path.join(sys.path[0], "assets", "audio")

class App:
    def __init__(self) -> None:
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("NeuroBeat")
        pygame.mouse.set_visible(True)
        self.clock  = pygame.time.Clock()
        self.width  = WIDTH
        self.height = HEIGHT

        # Data layer
        self.db: DatabaseManager = DatabaseManager()
        self.current_user = None
        self.current_score = 0
        self.session_id = None

        # Game engine (STT + validation) shared between all screens
        # Game engine (STT + validation) shared between all screens
        # We pass self.db to it so it can read the data
        self.engine: GameEngine = GameEngine(self.db)

        # Theme selected on the home screen (None = all themes)
        self.selected_theme: str | None = None

        # Screen registry — instantiated only once
        self._screens: dict[str, object] = {
            "splash": SplashScreen(self),
            "login":  LoginScreen(self),
            "home":   HomeScreen(self),
            "game":   GameScreen(self),
            "leaderboard": LeaderboardScreen(self),
            "stats":  StatsScreen(self),
        }

        # Direct start on the home screen instead of the splash/login
        self._active_key: str = "home"
        self._active          = self._screens["home"]
        self._active.on_enter()

        # --- 1v1 Mode (Blind Test) ---
        self.mode_1v1 = False         # False = Solo, True = 1v1
        self.nom_j1 = "Joueur 1"
        self.nom_j2 = "Joueur 2"
        self.score_j1 = 0
        self.score_j2 = 0
        self.buzzer_actif = None       # Will contain 'J1' or 'J2' during voice recognition

        self.nb_manches_totales = 3   
        self.manches_jouees = 0


    def go_to(self, key: str) -> None:
        """Navigates to a named screen."""
        if key not in self._screens:
            raise KeyError(f"Unknown screen: '{key}'")
        self._active.on_exit()
        self._active_key = key
        self._active     = self._screens[key]
        self._active.on_enter()
        
    def login(self, name: str) -> None:
        """Logs in the user and retrieves their score."""
        self.current_user = name
        
        # 1. We clean the database of any duplicates BEFORE loading
        self.db.clean_duplicate_profiles()
        
        # 2. We retrieve the profile (which is now guaranteed to be unique)
        profile = self.db.get_profile(name)
        
        if profile:
            self.current_score = profile['total_score']
        else:
            self.current_score = 0
            self.db.save_score(name, 0) # Creates the new user if they do not exist
            
        print(f"Logged in as: {self.current_user} | Score: {self.current_score}")

    def run(self) -> None:
        pygame.mouse.set_visible(False) # We hide the real defective mouse
        
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                self._active.handle_event(event)

            self._active.update(dt)
            self._active.draw()
            
            # --- DRAWS A MANUAL MOUSE ---
            mx, my = pygame.mouse.get_pos()
            pygame.draw.circle(self.screen, (255, 255, 255), (mx, my), 5) # A small white dot
            pygame.draw.circle(self.screen, (0, 0, 0), (mx, my), 5, 1)    # A black outline
            
            pygame.display.flip()