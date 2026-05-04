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
AUDIO_PATH = os.path.join(sys.path[0], "assets", "audio")

class App:
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("NeuroBeat")
        self.clock  = pygame.time.Clock()
        self.width  = WIDTH
        self.height = HEIGHT

        # Couche données
        self.db: DatabaseManager = DatabaseManager()
        self.current_user = None
        self.current_score = 0

        # Moteur de jeu (STT + validation) partagé entre tous les screens
        self.engine: GameEngine = GameEngine(language="en")

        # Thème sélectionné sur le home screen (None = tous les thèmes)
        self.selected_theme: str | None = None

        # Registre des écrans — instanciés une seule fois
        self._screens: dict[str, object] = {
            "splash": SplashScreen(self),
            "login":  LoginScreen(self),
            "home":   HomeScreen(self),
            "game":   GameScreen(self),
        }

        # Démarrage sur le splash
        self._active_key: str = "splash"
        self._active          = self._screens["splash"]
        self._active.on_enter()

    def go_to(self, key: str) -> None:
        """Navigue vers un écran nommé."""
        if key not in self._screens:
            raise KeyError(f"Unknown screen: '{key}'")
        self._active.on_exit()
        self._active_key = key
        self._active     = self._screens[key]
        self._active.on_enter()

    def run(self) -> None:
        """Boucle principale."""
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                self._active.handle_event(event)

            self._active.update(dt)
            self._active.draw()
            pygame.display.flip()

        # Start on the splash screen
        self._active_key: str = "splash"
        self._active = self._screens["splash"]
        self._active.on_enter()
            
    def login(self, name):
        # Logic to set the current active profile
        self.current_user = name
        print(f"Logged in as: {self.current_user}")