"""
NeuroBeat — Splash screen.
"""

from __future__ import annotations
import pygame
from src.screens.base_screen import BaseScreen
from src.constants import C_BG, C_WHITE, C_GOLD, SPLASH_DURATION
from src.widgets import MusicStaff, blit_centered


class SplashScreen(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._timer = 0.0
        self._font_big  = pygame.font.SysFont("Arial", 72, bold=True)
        self._font_sub  = pygame.font.SysFont("Arial", 22)
        self._staff     = MusicStaff(self.screen, 80, self.H // 2 + 80, self.W - 160)

    def on_enter(self) -> None:
        self._timer = 0.0

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.app.go_to("home")

    def update(self, dt: float) -> None:
        self._timer += dt
        self._staff.update(dt)
        if self._timer >= SPLASH_DURATION:
            self.app.go_to("home")

    def draw(self) -> None:
        self.screen.fill(C_BG)
        self._draw_dot_grid()

        # Titre principal
        surf = self._font_big.render("NEUROBEAT", True, C_GOLD)
        blit_centered(self.screen, surf, self.W // 2, self.H // 2 - 60)

        # Sous-titre
        sub = self._font_sub.render("Le blind-test qui réveille tes neurones", True, C_WHITE)
        blit_centered(self.screen, sub, self.W // 2, self.H // 2 + 20)

        # Staff animé
        self._staff.draw()
