"""
NeuroBeat — Home screen.
Affiche le titre, un sélecteur de thème (carrousel) et le bouton COMMENCER.
"""

from __future__ import annotations
import pygame
from src.screens.base_screen import BaseScreen
from src.constants import C_BG, C_GOLD, C_WHITE, C_BTN, C_BTN_HOVER, C_GREY, C_BORDER, C_PANEL
from src.widgets import Button, MusicStaff, draw_rounded_rect, blit_centered


class HomeScreen(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._font_title  = pygame.font.SysFont("Arial", 62, bold=True)
        self._font_sub    = pygame.font.SysFont("Arial", 20)
        self._font_btn    = pygame.font.SysFont("Arial", 26, bold=True)
        self._font_theme  = pygame.font.SysFont("Arial", 22, bold=True)  # légèrement plus grand
        self._font_small  = pygame.font.SysFont("Arial", 18)

        cx = self.W // 2

        # --- Boutons d'action ---
        self._btn_play = Button(
            pygame.Rect(cx - 120, self.H - 180, 240, 60),
            "START",
            self._font_btn,
        )
        self._btn_leaderboard = Button(
            pygame.Rect(cx - 120, self.H - 130, 240, 50),
            "LEADERBOARD",
            self._font_btn,
        )
        self._btn_stats = Button(
            pygame.Rect(cx - 120, self.H - 80, 240, 44),
            "STATISTICS",
            self._font_btn,
            colour=C_BTN,
            hover_colour=C_BTN_HOVER,
        )

        # --- Carrousel : boutons fléchés gauche / droite ---
        arrow_y    = self.H // 2 + 10      # même zone verticale qu'avant
        arrow_size = 44

        self._btn_prev = Button(
            pygame.Rect(cx - 200, arrow_y, arrow_size, arrow_size),
            "◀",
            self._font_btn,
            colour=C_PANEL,
            hover_colour=C_BTN_HOVER,
            border_colour=C_BORDER,
        )
        self._btn_next = Button(
            pygame.Rect(cx + 200 - arrow_size, arrow_y, arrow_size, arrow_size),
            "▶",
            self._font_btn,
            colour=C_PANEL,
            hover_colour=C_BTN_HOVER,
            border_colour=C_BORDER,
        )

        # Rectangle de la "vitrine" du thème sélectionné (centré entre les deux flèches)
        self._theme_rect = pygame.Rect(cx - 140, arrow_y, 280, arrow_size)

        # Liste des thèmes et index courant
        self._themes: list[str] = []
        self._theme_index: int  = 0

        self._staff = MusicStaff(self.screen, 60, self.H - 60, self.W - 120, amplitude=18)

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        self._themes = ["ALL"] + self.db.get_themes()

        # Retrouve l'index correspondant au thème mémorisé dans app
        current = self.app.selected_theme or "ALL"
        if current in self._themes:
            self._theme_index = self._themes.index(current)
        else:
            self._theme_index = 0

        self._sync_app_theme()

    def on_exit(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _sync_app_theme(self) -> None:
        """Met à jour app.selected_theme depuis l'index courant."""
        selected = self._themes[self._theme_index]
        self.app.selected_theme = None if selected == "ALL" else selected

    def _prev_theme(self) -> None:
        self._theme_index = (self._theme_index - 1) % len(self._themes)
        self._sync_app_theme()

    def _next_theme(self) -> None:
        self._theme_index = (self._theme_index + 1) % len(self._themes)
        self._sync_app_theme()

    # ------------------------------------------------------------------
    # Gestion des événements
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.app.go_to("game")
            elif event.key == pygame.K_LEFT:
                self._prev_theme()
            elif event.key == pygame.K_RIGHT:
                self._next_theme()

        if self._btn_play.handle_event(event):
            self.app.go_to("game")
        if self._btn_leaderboard.handle_event(event):
            self.app.go_to("leaderboard")
        if self._btn_stats.handle_event(event):
            self.app.go_to("stats")

        # Flèches du carrousel
        if self._btn_prev.handle_event(event):
            self._prev_theme()
        if self._btn_next.handle_event(event):
            self._next_theme()

    # ------------------------------------------------------------------
    # Update / Draw
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self._staff.update(dt)

    def draw(self) -> None:
        self.screen.fill(C_BG)
        self._draw_dot_grid()

        # Profil utilisateur
        if self.app.current_user:
            profile_text = f"Player: {self.app.current_user} | Score: {self.app.current_score}"
            surf_profile = self._font_sub.render(profile_text, True, C_WHITE)
            self.screen.blit(surf_profile, (20, 20))

        # Titre
        surf = self._font_title.render("NEUROBEAT", True, C_GOLD)
        blit_centered(self.screen, surf, self.W // 2, 100)

        sub = self._font_sub.render("Choose a theme and prove your music knowledge !", True, C_GREY)
        blit_centered(self.screen, sub, self.W // 2, 180)

        # Label "THEME"
        lbl = self._font_sub.render("THEME", True, C_GOLD)
        blit_centered(self.screen, lbl, self.W // 2, self.H // 2 - 10)

        # --- Carrousel ---
        self._draw_carousel()

        # Boutons d'action + staff
        self._staff.draw()
        self._btn_play.draw(self.screen)
        self._btn_leaderboard.draw(self.screen)
        self._btn_stats.draw(self.screen)

    def _draw_carousel(self) -> None:
        """Dessine la vitrine du thème courant + les deux flèches."""
        if not self._themes:
            return

        # Fond doré (bordure active) derrière la vitrine
        draw_rounded_rect(
            self.screen, C_GOLD,
            self._theme_rect.inflate(4, 4), 12,
        )
        # Fond intérieur
        draw_rounded_rect(
            self.screen, C_PANEL,
            self._theme_rect, 10,
        )

        # Texte du thème courant
        label = self._themes[self._theme_index].upper()
        surf  = self._font_theme.render(label, True, C_GOLD)
        blit_centered(
            self.screen, surf,
            self._theme_rect.centerx,
            self._theme_rect.centery,
        )

        # Indicateur de position  ex: "2 / 5"
        indicator = f"{self._theme_index + 1} / {len(self._themes)}"
        surf_ind  = self._font_small.render(indicator, True, C_GREY)
        blit_centered(
            self.screen, surf_ind,
            self._theme_rect.centerx,
            self._theme_rect.bottom + 16,
        )

        # Flèches
        self._btn_prev.draw(self.screen)
        self._btn_next.draw(self.screen)