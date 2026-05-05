"""
NeuroBeat — Home screen.
Affiche le titre, un sélecteur de thème et le bouton COMMENCER.
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
        self._font_theme  = pygame.font.SysFont("Arial", 18)

        cx = self.W // 2

        self._btn_play = Button(
            pygame.Rect(cx - 120, self.H - 160, 240, 60),
            "START",
            self._font_btn,
        )
        
        self._btn_leaderboard = Button(
            pygame.Rect(cx - 120, self.H - 110, 240, 50), # Placed slightly lower
            "LEADERBOARD",
            self._font_btn,
        )

        # Boutons thème (générés dynamiquement depuis la DB)
        self._themes:      list[str]   = []
        self._theme_btns:  list[Button] = []
        self._staff = MusicStaff(self.screen, 60, self.H - 60, self.W - 120, amplitude=18)

    def on_enter(self) -> None:
        # Recharge les thèmes à chaque visite (la DB peut avoir été modifiée)
        self._themes     = ["ALL"] + self.db.get_themes()
        self._theme_btns = self._build_theme_buttons()

        # Sélection par défaut
        if self.app.selected_theme not in self._themes:
            self.app.selected_theme = self._themes[0]

    def on_exit(self) -> None:
        pass

    def _build_theme_buttons(self) -> list[Button]:
        """Crée un bouton par thème, centrés horizontalement."""
        btns   = []
        btn_w  = 140
        btn_h  = 40
        gap    = 12
        total  = len(self._themes) * btn_w + (len(self._themes) - 1) * gap
        start_x = self.W // 2 - total // 2
        y       = self.H // 2 + 30

        for i, theme in enumerate(self._themes):
            x = start_x + i * (btn_w + gap)
            btns.append(Button(
                pygame.Rect(x, y, btn_w, btn_h),
                theme.upper(),
                self._font_theme,
                colour=C_PANEL,
                hover_colour=C_BTN_HOVER,
                border_colour=C_BORDER,
            ))
        return btns

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.app.go_to("game")

        if self._btn_play.handle_event(event):
            self.app.go_to("game")
        
        if self._btn_leaderboard.handle_event(event):
            self.app.go_to("leaderboard")

        for i, btn in enumerate(self._theme_btns):
            if btn.handle_event(event):
                selected = self._themes[i]
                self.app.selected_theme = None if selected == "ALL" else selected

    def update(self, dt: float) -> None:
        self._staff.update(dt)

    def draw(self) -> None:
        self.screen.fill(C_BG)
        self._draw_dot_grid()
        
        # --- Affichage du profil utilisateur ---
        if self.app.current_user:
            profile_text = f"Player: {self.app.current_user} | Score: {self.app.current_score}"
            surf_profile = self._font_sub.render(profile_text, True, C_WHITE)
            # Affichage en haut à gauche
            self.screen.blit(surf_profile, (20, 20))

        # Titre
        surf = self._font_title.render("NEUROBEAT", True, C_GOLD)
        blit_centered(self.screen, surf, self.W // 2, 100)

        sub = self._font_sub.render("Choose a theme and prove your music knowledge !", True, C_GREY)
        blit_centered(self.screen, sub, self.W // 2, 180)

        # Label thèmes
        lbl = self._font_sub.render("THEME", True, C_GOLD)
        blit_centered(self.screen, lbl, self.W // 2, self.H // 2 - 10)

        # Boutons thème
        for i, btn in enumerate(self._theme_btns):
            # Surligne le thème actif
            theme = self._themes[i]
            is_active = (
                (theme == "ALL" and self.app.selected_theme is None) or
                (theme == self.app.selected_theme)
            )
            if is_active:
                # Bordure or plus épaisse pour le thème actif
                draw_rounded_rect(
                    self.screen, C_GOLD,
                    btn.rect.inflate(4, 4), 12,
                )
            btn.draw(self.screen)

        # Bouton jouer
        self._staff.draw()

        self._btn_play.draw(self.screen)
        self._btn_leaderboard.draw(self.screen)

        # Staff animé en bas
        
    def _build_theme_buttons(self) -> list[Button]:
        """Crée un bouton par thème, répartis sur plusieurs lignes centrées."""
        btns   = []
        btn_w  = 140
        btn_h  = 40
        gap_x  = 12
        gap_y  = 15
        max_per_row = 6 # Nombre maximum de boutons par ligne avant de passer à la suite

        # Position Y de départ pour les boutons
        base_y = self.H // 2 + 10

        # Diviser la liste complète des thèmes en plusieurs lignes (chunks)
        rows = [self._themes[i:i + max_per_row] for i in range(0, len(self._themes), max_per_row)]

        for row_idx, row_themes in enumerate(rows):
            # Calculer la largeur totale de cette ligne spécifique pour bien la centrer
            total_w = len(row_themes) * btn_w + (len(row_themes) - 1) * gap_x
            start_x = self.W // 2 - total_w // 2
            current_y = base_y + row_idx * (btn_h + gap_y)

            for col_idx, theme in enumerate(row_themes):
                x = start_x + col_idx * (btn_w + gap_x)
                btns.append(Button(
                    pygame.Rect(x, current_y, btn_w, btn_h),
                    theme.upper(),
                    self._font_theme,
                    colour=C_PANEL,
                    hover_colour=C_BTN_HOVER,
                    border_colour=C_BORDER,
                ))
        return btns