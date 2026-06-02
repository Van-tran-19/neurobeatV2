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

        # États de configuration pour le menu
        self.ETAT_MENU_PRINCIPAL = "menu"
        self.ETAT_CHOIX_JOUEURS  = "choix_joueurs"
        self.ETAT_SAISIE_J1      = "saisie_j1"
        self.ETAT_SAISIE_J2      = "saisie_j2"
        self.menu_state = self.ETAT_MENU_PRINCIPAL

        # Variables temporaires pour la saisie de texte
        self._input_name_j1 = ""
        self._input_name_j2 = ""

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
        # 1. Gestion des clics sur les boutons du carrousel de thèmes (toujours actifs)
        if self._btn_prev.handle_event(event):
            self._prev_theme()
            return
        if self._btn_next.handle_event(event):
            self._next_theme()
            return

        # 2. Gestion selon l'état actuel du menu de configuration
        if self.menu_state == self.ETAT_MENU_PRINCIPAL:
            # Clic sur START -> On passe au choix du mode (Solo / 1v1)
            if self._btn_play.handle_event(event):
                self.menu_state = self.ETAT_CHOIX_JOUEURS
                return
            
            # Clic sur LEADERBOARD
            if self._btn_leaderboard.handle_event(event):
                self.app.go_to("leaderboard")
                return
            
            # Clic sur STATISTICS
            if self._btn_stats.handle_event(event):
                self.app.go_to("stats")
                return

        elif self.menu_state == self.ETAT_CHOIX_JOUEURS:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    self.app.mode_1v1 = False
                    self.menu_state = self.ETAT_SAISIE_J1
                elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    self.app.mode_1v1 = True
                    self.menu_state = self.ETAT_SAISIE_J1
                elif event.key == pygame.K_ESCAPE:
                    self.menu_state = self.ETAT_MENU_PRINCIPAL

        elif self.menu_state == self.ETAT_SAISIE_J1:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self._input_name_j1.strip():
                    self.app.nom_j1 = self._input_name_j1.strip()
                    if self.app.mode_1v1:
                        self.menu_state = self.ETAT_SAISIE_J2
                    else:
                        # Mode Solo : initialisations et lancement du jeu
                        self.app.nom_j2 = ""
                        self.app.current_user = self.app.nom_j1
                        self.app.go_to("game")
                elif event.key == pygame.K_BACKSPACE:
                    self._input_name_j1 = self._input_name_j1[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.menu_state = self.ETAT_CHOIX_JOUEURS
                else:
                    # Enregistre les caractères tapés (limité à 15 caractères)
                    if event.unicode and len(self._input_name_j1) < 15:
                        self._input_name_j1 += event.unicode

        elif self.menu_state == self.ETAT_SAISIE_J2:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self._input_name_j2.strip():
                    self.app.nom_j2 = self._input_name_j2.strip()
                    # Lancement du jeu en mode 1v1
                    self.app.go_to("game")
                elif event.key == pygame.K_BACKSPACE:
                    self._input_name_j2 = self._input_name_j2[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.menu_state = self.ETAT_SAISIE_J1
                else:
                    if event.unicode and len(self._input_name_j2) < 15:
                        self._input_name_j2 += event.unicode
    # ------------------------------------------------------------------
    # Update / Draw
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self._staff.update(dt)

    def draw(self) -> None:
        self.screen.fill(C_BG)
        self._draw_dot_grid()

        # Profil utilisateur
        # Profil utilisateur + Score global ou Scores du 1v1 actuel
        if self.app.mode_1v1:
            hud_text = f"🎮 {self.app.nom_j1}: {self.app.score_j1} pts   VS   {self.app.nom_j2}: {self.app.score_j2} pts"
            surf_profile = self._font_sub.render(hud_text, True, C_GOLD)
            self.screen.blit(surf_profile, (20, 20))
        elif self.app.current_user:
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

        # --- Superposition des écrans de configuration ---
        if self.menu_state != self.ETAT_MENU_PRINCIPAL:
            # Assombrir l'écran en arrière-plan
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((15, 15, 26, 240))
            self.screen.blit(overlay, (0, 0))

            if self.menu_state == self.ETAT_CHOIX_JOUEURS:
                t1 = self._font_title.render("MODE DE JEU", True, C_GOLD)
                t2 = self._font_btn.render("Appuyez sur [1] pour SOLO  ou  [2] pour 1v1", True, C_WHITE)
                blit_centered(self.screen, t1, self.W // 2, self.H // 2 - 50)
                blit_centered(self.screen, t2, self.W // 2, self.H // 2 + 30)

            elif self.menu_state == self.ETAT_SAISIE_J1:
                titre_saisie = "MODE SOLO" if not self.app.mode_1v1 else "JOUEUR 1 (1v1)"
                t1 = self._font_title.render(titre_saisie, True, C_GOLD)
                t2 = self._font_btn.render(f"Entrez votre nom : {self._input_name_j1}_", True, C_WHITE)
                t3 = self._font_small.render("Appuyez sur [Entrée] pour valider", True, C_GREY)
                blit_centered(self.screen, t1, self.W // 2, self.H // 2 - 60)
                blit_centered(self.screen, t2, self.W // 2, self.H // 2)
                blit_centered(self.screen, t3, self.W // 2, self.H // 2 + 60)

            elif self.menu_state == self.ETAT_SAISIE_J2:
                t1 = self._font_title.render("JOUEUR 2", True, C_GOLD)
                t2 = self._font_btn.render(f"Entrez votre nom : {self._input_name_j2}_", True, C_WHITE)
                t3 = self._font_small.render("Appuyez sur [Entrée] pour valider", True, C_GREY)
                blit_centered(self.screen, t1, self.W // 2, self.H // 2 - 60)
                blit_centered(self.screen, t2, self.W // 2, self.H // 2)
                blit_centered(self.screen, t3, self.W // 2, self.H // 2 + 60)

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