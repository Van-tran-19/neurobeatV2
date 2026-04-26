"""
NeuroBeat — Application controller.

Owns the pygame window, the clock, the database instance and the screen
registry. All screen navigation goes through `app.go_to(key)`.
"""

from __future__ import annotations
import pygame
from src.constants import WIDTH, HEIGHT, FPS
from data.database import DatabaseManager
from src.screens.splash_screen import SplashScreen
from src.screens.home_screen import HomeScreen
from src.screens.game_screen import GameScreen


class App:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("NeuroBeat")
        self.clock  = pygame.time.Clock()
        self.width  = WIDTH
        self.height = HEIGHT

        # Shared data layer — injected into every screen
        self.db: DatabaseManager = DatabaseManager()

        # Shared state between screens
        self.selected_theme: str = self.db.get_themes()[0]

        # Screen registry — screens are instantiated once and reused
        self._screens: dict[str, object] = {
            "splash": SplashScreen(self),
            "home":   HomeScreen(self),
            "game":   GameScreen(self),
        }

        # Start on the splash screen
        self._active_key: str = "splash"
        self._active = self._screens["splash"]
        self._active.on_enter()

    def go_to(self, key: str) -> None:
        """Navigate to a named screen."""
        if key not in self._screens:
            raise KeyError(f"Unknown screen: '{key}'")
        self._active.on_exit()
        self._active_key = key
        self._active     = self._screens[key]
        self._active.on_enter()

    def run(self) -> None:
        """Main game loop."""
        while True:
            dt = self.clock.tick(FPS) / 1000.0   # seconds since last frame

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                self._active.handle_event(event)

            self._active.update(dt)
            self._active.draw()
            pygame.display.flip()
