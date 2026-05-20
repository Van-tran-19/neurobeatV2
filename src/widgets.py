"""
NeuroBeat — Reusable UI widgets.
All widgets are stateless or self-contained so they can be composed freely
across different screens.
"""

from __future__ import annotations
import pygame
import math
from src.constants import *


# ── Drawing primitives ────────────────────────────────────────────────────────

def draw_rounded_rect(
    surface: pygame.Surface,
    colour: tuple,
    rect: pygame.Rect,
    radius: int = 12,
    alpha: int | None = None,
    border_colour: tuple | None = None,
    border_width: int = 0,
) -> None:
    """Filled rounded rectangle with modern shadow, optional alpha and border."""
    # 1. Ombre portée (Shadow) douce
    shadow_rect = pygame.Rect(rect.x + 2, rect.y + 6, rect.width, rect.height)
    pygame.draw.rect(surface, (8, 12, 22), shadow_rect, border_radius=radius)

    # 2. Panneau principal
    if alpha is not None:
        tmp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(tmp, (*colour[:3], alpha), tmp.get_rect(), border_radius=radius)
        surface.blit(tmp, rect.topleft)
    else:
        pygame.draw.rect(surface, colour, rect, border_radius=radius)

    # 3. Bordure
    if border_colour and border_width > 0:
        pygame.draw.rect(surface, border_colour, rect, border_width, border_radius=radius)


def blit_centered(
    surface: pygame.Surface,
    text_surf: pygame.Surface,
    cx: int,
    y: int,
) -> None:
    """Blit a rendered surface horizontally centered on cx."""
    surface.blit(text_surf, (cx - text_surf.get_width() // 2, y))


# ── Widgets ───────────────────────────────────────────────────────────────────

class Panel:
    """Card panel with bold title, separator and body lines."""

    def __init__(
        self,
        rect: pygame.Rect,
        title: str = "",
        font_title: pygame.font.Font | None = None,
        font_body: pygame.font.Font | None = None,
        colour: tuple = C_PANEL,
        border_colour: tuple = C_BORDER,
        border_width: int = 2,
        radius: int = 16,
        title_colour: tuple = C_WHITE,
        body_colour: tuple = C_GREY,
        line_height_extra: int = 4,
    ) -> None:
        self.rect              = rect
        self.title             = title
        self.font_title        = font_title
        self.font_body         = font_body
        self.colour            = colour
        self.border_colour     = border_colour
        self.border_width      = border_width
        self.radius            = radius
        self.title_colour      = title_colour
        self.body_colour       = body_colour
        self.line_height_extra = line_height_extra
        self.lines: list[str]  = []

    def set_lines(self, lines: list[str]) -> None:
        self.lines = lines

    def draw(self, surface: pygame.Surface) -> None:
        draw_rounded_rect(
            surface, self.colour, self.rect, self.radius,
            border_colour=self.border_colour, border_width=self.border_width,
        )

        y = self.rect.y + 16

        if self.title and self.font_title:
            surf = self.font_title.render(self.title, True, self.title_colour)
            blit_centered(surface, surf, self.rect.centerx, y)
            y += surf.get_height() + 10
            pygame.draw.line(
                surface, self.border_colour,
                (self.rect.x + 16, y), (self.rect.right - 16, y), 2,
            )
            y += 12

        if self.font_body:
            lh = self.font_body.get_linesize() + self.line_height_extra
            for line in self.lines:
                surf = self.font_body.render(line, True, self.body_colour)
                surface.blit(surf, (self.rect.x + 16, y))
                y += lh


class Button:
    """Clickable button with hover state and 3D animation."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        colour: tuple = C_BTN,
        hover_colour: tuple = C_BTN_HOVER,
        text_colour: tuple = C_WHITE,
        radius: int = 12,
        border_colour: tuple | None = C_BORDER,
        border_width: int = 0,
    ) -> None:
        self.rect          = pygame.Rect(rect)
        self.text          = text
        self.font          = font
        self.colour        = colour
        self.hover_colour  = hover_colour
        self.text_colour   = text_colour
        self.radius        = radius
        self.border_colour = border_colour
        self.border_width  = border_width
        self._hovered      = False
        self._pressed      = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
            if not self._hovered:
                self._pressed = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hovered:
                self._pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self._hovered:
                self._pressed = False
                return True
            self._pressed = False
        return False

    def draw(self, surface: pygame.Surface) -> None:
        current_colour = self.hover_colour if self._hovered else self.colour
        
        # Animation : le bouton descend de 3 pixels quand on clique
        y_offset = 3 if self._pressed else 0
        display_rect = pygame.Rect(self.rect.x, self.rect.y + y_offset, self.rect.width, self.rect.height)

        # Tranche 3D / Ombre (visible uniquement quand le bouton n'est pas cliqué)
        if not self._pressed:
            shadow_rect = pygame.Rect(self.rect.x, self.rect.y + 4, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, (49, 46, 129), shadow_rect, border_radius=self.radius) 

        # Corps du bouton
        pygame.draw.rect(surface, current_colour, display_rect, border_radius=self.radius)
        
        # Effet "Reflet" très léger en haut du bouton pour donner du volume
        pygame.draw.rect(surface, (120, 130, 255), display_rect, width=1, border_radius=self.radius)

        # Texte centré
        text_surf = self.font.render(self.text, True, self.text_colour)
        text_y = display_rect.centery - text_surf.get_height() // 2
        blit_centered(surface, text_surf, display_rect.centerx, text_y)


class ProgressBar:
    """Horizontal progress bar with rounded ends."""

    def __init__(
        self,
        rect: pygame.Rect,
        colour: tuple = C_GOLD,
        bg_colour: tuple = C_PANEL,
        radius: int = 10,
    ) -> None:
        self.rect      = rect
        self.colour    = colour
        self.bg_colour = bg_colour
        self.radius    = radius
        self.progress  = 1.0   # 0.0 → 1.0

    def draw(self, surface: pygame.Surface) -> None:
        # Fond
        pygame.draw.rect(surface, self.bg_colour, self.rect, border_radius=self.radius)
        # Remplissage
        if self.progress > 0.02:
            fill_w = max(self.radius * 2, int(self.rect.width * self.progress))
            fill = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
            pygame.draw.rect(surface, self.colour, fill, border_radius=self.radius)


class MusicStaff:
    """
    Animated decorative musical staff with note heads.
    Reproduces the wavy staff-with-notes motif from the PDF mockups.
    """

    def __init__(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        amplitude: int = 28,
        speed: float = 0.35,
        note_positions: list[float] | None = None,
    ) -> None:
        self.surface   = surface
        self.x         = x
        self.y         = y
        self.width     = width
        self.amplitude = amplitude
        self.speed     = speed
        self._t        = 0.0
        self._note_pos = note_positions or [
            0.06, 0.15, 0.25, 0.36, 0.48, 0.59, 0.70, 0.81, 0.91,
        ]

    def update(self, dt: float) -> None:
        self._t += dt * self.speed

    def _wave_y(self, frac: float) -> int:
        return self.y + int(self.amplitude * math.sin(frac * math.pi * 2 + self._t * 2 * math.pi))

    def draw(self) -> None:
        steps    = self.width // 3
        line_gap = 9

        # Cinq lignes de portée
        for li in range(5):
            offset = (li - 2) * line_gap
            pts = [
                (self.x + int(i / steps * self.width),
                 self._wave_y(i / steps) + offset)
                for i in range(steps + 1)
            ]
            if len(pts) >= 2:
                pygame.draw.lines(self.surface, C_NOTE_LINE, False, pts, 2)

        # Têtes de notes avec hampes et crochets
        for frac in self._note_pos:
            cx = self.x + int(frac * self.width)
            cy = self._wave_y(frac)

            head = pygame.Rect(cx - 9, cy - 6, 18, 12)
            pygame.draw.ellipse(self.surface, C_NOTE_FILL, head)
            pygame.draw.ellipse(self.surface, C_NOTE_LINE, head, 2)

            pygame.draw.line(self.surface, C_NOTE_LINE, (cx + 8, cy), (cx + 8, cy - 28), 2)

            pygame.draw.arc(
                self.surface, C_NOTE_LINE,
                pygame.Rect(cx + 8, cy - 28, 14, 14),
                0, math.pi, 2,
            )