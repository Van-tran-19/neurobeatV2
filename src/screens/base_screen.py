"""
NeuroBeat — Abstract base class for all screens.
Every screen receives a reference to the App (for navigation, fonts, DB, engine)
and must implement the three lifecycle methods below.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
from src.constants import C_DOT_GRID


class BaseScreen(ABC):
    def __init__(self, app: "App") -> None:  # type: ignore[name-defined]
        self.app    = app
        self.screen = app.screen
        self.W      = app.width
        self.H      = app.height
        self.db     = app.db
        self.engine = app.engine   # GameEngine partagé

    # ── Lifecycle hooks ──────────────────────────────────────────────────────

    def on_enter(self) -> None:
        """Appelé chaque fois que cet écran devient actif."""

    def on_exit(self) -> None:
        """Appelé chaque fois que cet écran est désactivé."""

    # ── Interface obligatoire ────────────────────────────────────────────────

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self) -> None: ...

    # ── Helpers partagés ─────────────────────────────────────────────────────

    def _blit(
        self,
        text: str,
        font: pygame.font.Font,
        colour: tuple,
        pos: tuple[int, int],
        *,
        center_x: bool = False,
        alpha: int = 255,
    ) -> pygame.Rect:
        surf = font.render(text, True, colour)
        if alpha < 255:
            surf.set_alpha(alpha)
        x, y = pos
        if center_x:
            x -= surf.get_width() // 2
        self.screen.blit(surf, (x, y))
        return surf.get_rect(topleft=(x, y))

    def _blit_multiline(
        self,
        text: str,
        font: pygame.font.Font,
        colour: tuple,
        rect: pygame.Rect,
        line_spacing: int = 4,
    ) -> None:
        words, lines, current = text.split(), [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if font.size(candidate)[0] <= rect.width:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)

        lh = font.get_linesize() + line_spacing
        for i, line in enumerate(lines):
            surf = font.render(line, True, colour)
            self.screen.blit(surf, (rect.x, rect.y + i * lh))

    def _draw_dot_grid(self, spacing: int = 50, colour: tuple = C_DOT_GRID) -> None:
        for gx in range(0, self.W, spacing):
            for gy in range(0, self.H, spacing):
                pygame.draw.circle(self.screen, colour, (gx, gy), 1)
    def draw(self) -> None: ...

    # ── Shared drawing helpers available to all screens ──────────────────

    def _blit(
        self,
        text: str,
        font: pygame.font.Font,
        colour: tuple,
        pos: tuple[int, int],
        *,
        center_x: bool = False,
        alpha: int = 255,
    ) -> pygame.Rect:
        """Render and blit text. Returns the bounding rect."""
        surf = font.render(text, True, colour)
        if alpha < 255:
            surf.set_alpha(alpha)
        x, y = pos
        if center_x:
            x -= surf.get_width() // 2
        self.screen.blit(surf, (x, y))
        return surf.get_rect(topleft=(x, y))

    def _blit_multiline(
        self,
        text: str,
        font: pygame.font.Font,
        colour: tuple,
        rect: pygame.Rect,
        line_spacing: int = 4,
    ) -> None:
        """Word-wrap *text* inside *rect* and blit each line."""
        words, lines, current = text.split(), [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if font.size(candidate)[0] <= rect.width:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)

        lh = font.get_linesize() + line_spacing
        for i, line in enumerate(lines):
            surf = font.render(line, True, colour)
            self.screen.blit(surf, (rect.x, rect.y + i * lh))

    def _draw_dot_grid(self, spacing: int = 50, colour: tuple = (48, 52, 175)) -> None:
        """Subtle dot-grid background decoration."""
        for gx in range(0, self.W, spacing):
            for gy in range(0, self.H, spacing):
                pygame.draw.circle(self.screen, colour, (gx, gy), 1)
