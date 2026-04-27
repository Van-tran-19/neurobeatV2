"""
NeuroBeat — Reusable UI widgets.
All widgets are stateless or self-contained so they can be composed freely
across different screens.
"""

from __future__ import annotations
import pygame
import math
from constants import (
    C_PANEL, C_BORDER, C_GOLD, C_WHITE, C_GREY,
    C_BTN, C_BTN_HOVER, C_NOTE_FILL, C_NOTE_LINE,
)


# ── Drawing primitives ───────────────────────────────────────────────────────

def draw_rounded_rect(
    surface: pygame.Surface,
    colour: tuple,
    rect: pygame.Rect,
    radius: int = 10,
    alpha: int | None = None,
    border_colour: tuple | None = None,
    border_width: int = 0,
) -> None:
    """Filled rounded rectangle with optional alpha and border."""
    if alpha is not None:
        tmp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(tmp, (*colour[:3], alpha), tmp.get_rect(), border_radius=radius)
        surface.blit(tmp, rect.topleft)
    else:
        pygame.draw.rect(surface, colour, rect, border_radius=radius)

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


# ── Widgets ──────────────────────────────────────────────────────────────────

class Panel:
    """
    A card panel with a bold title, a gold separator, and a list of body lines.
    Matches the card style in the PDF game-screen mockup.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        title: str = "",
        font_title: pygame.font.Font | None = None,
        font_body: pygame.font.Font | None = None,
        colour: tuple = C_PANEL,
        border_colour: tuple = C_BORDER,
        border_width: int = 2,
        radius: int = 8,
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
        # Background + border
        draw_rounded_rect(
            surface, self.colour, self.rect, self.radius,
            border_colour=self.border_colour, border_width=self.border_width,
        )

        y = self.rect.y + 12

        # Title row
        if self.title and self.font_title:
            surf = self.font_title.render(self.title, True, self.title_colour)
            blit_centered(surface, surf, self.rect.centerx, y)
            y += surf.get_height() + 6
            # Separator
            pygame.draw.line(
                surface, self.border_colour,
                (self.rect.x + 8, y), (self.rect.right - 8, y), 1,
            )
            y += 8

        # Body lines
        if self.font_body:
            lh = self.font_body.get_linesize() + self.line_height_extra
            for line in self.lines:
                surf = self.font_body.render(line, True, self.body_colour)
                surface.blit(surf, (self.rect.x + 12, y))
                y += lh


class Button:
    """Clickable button with hover state."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        colour: tuple = C_BTN,
        hover_colour: tuple = C_BTN_HOVER,
        text_colour: tuple = C_WHITE,
        radius: int = 10,
        border_colour: tuple | None = C_BORDER,
        border_width: int = 2,
    ) -> None:
        self.rect          = rect
        self.text          = text
        self.font          = font
        self.colour        = colour
        self.hover_colour  = hover_colour
        self.text_colour   = text_colour
        self.radius        = radius
        self.border_colour = border_colour
        self.border_width  = border_width
        self._hovered      = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if the button was clicked this event."""
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        colour = self.hover_colour if self._hovered else self.colour
        draw_rounded_rect(
            surface, colour, self.rect, self.radius,
            border_colour=self.border_colour, border_width=self.border_width,
        )
        surf = self.font.render(self.text, True, self.text_colour)
        blit_centered(surface, surf, self.rect.centerx, self.rect.centery - surf.get_height() // 2)


class ProgressBar:
    """Horizontal progress bar with rounded ends."""

    def __init__(
        self,
        rect: pygame.Rect,
        colour: tuple = C_GOLD,
        bg_colour: tuple = C_PANEL,
        radius: int = 6,
    ) -> None:
        self.rect      = rect
        self.colour    = colour
        self.bg_colour = bg_colour
        self.radius    = radius
        self.progress  = 1.0   # 0.0 → 1.0

    def draw(self, surface: pygame.Surface) -> None:
        draw_rounded_rect(surface, self.bg_colour, self.rect, self.radius)
        if self.progress > 0.0:
            fill_w = max(self.radius * 2, int(self.rect.width * self.progress))
            fill   = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
            draw_rounded_rect(surface, self.colour, fill, self.radius)


class MusicStaff:
    """
    Animated decorative musical staff with note heads.
    Reproduces the wavy staff-with-notes motif seen in the PDF mockups.
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

        # Fractional positions along the staff where notes appear (0–1)
        self._note_pos = note_positions or [
            0.06, 0.15, 0.25, 0.36, 0.48, 0.59, 0.70, 0.81, 0.91,
        ]

    def update(self, dt: float) -> None:
        self._t += dt * self.speed

    def _wave_y(self, frac: float) -> int:
        return self.y + int(self.amplitude * math.sin(frac * math.pi * 2 + self._t * 2 * math.pi))

    def draw(self) -> None:
        steps = self.width // 3
        line_gap = 9

        # Five staff lines
        for li in range(5):
            offset = (li - 2) * line_gap
            pts = [
                (self.x + int(i / steps * self.width),
                 self._wave_y(i / steps) + offset)
                for i in range(steps + 1)
            ]
            if len(pts) >= 2:
                pygame.draw.lines(self.surface, C_NOTE_LINE, False, pts, 2)

        # Note heads with stems and flags
        for frac in self._note_pos:
            cx = self.x + int(frac * self.width)
            cy = self._wave_y(frac)

            # Head
            head = pygame.Rect(cx - 9, cy - 6, 18, 12)
            pygame.draw.ellipse(self.surface, C_NOTE_FILL, head)
            pygame.draw.ellipse(self.surface, C_NOTE_LINE, head, 2)

            # Stem
            pygame.draw.line(self.surface, C_NOTE_LINE, (cx + 8, cy), (cx + 8, cy - 28), 2)

            # Simple flag
            flag_top = (cx + 8, cy - 28)
            pygame.draw.arc(
                self.surface, C_NOTE_LINE,
                pygame.Rect(cx + 8, cy - 28, 14, 14),
                0, math.pi, 2,
            )
