"""
NeuroBeat — Écran de statistiques cognitives.
Affiche les métriques de performance et de réactivité du patient/joueur.
"""
from __future__ import annotations
import pygame

from src.screens.base_screen import BaseScreen
from src.constants import C_BG, C_PANEL, C_BORDER, C_GOLD, C_WHITE, C_GREY, C_BTN, C_BTN_HOVER
from src.widgets import draw_rounded_rect, blit_centered, Button, Panel

class StatsScreen(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)

        self._font_title = pygame.font.SysFont("Arial", 40, bold=True)
        self._font_med   = pygame.font.SysFont("Arial", 24)
        self._font_small = pygame.font.SysFont("Arial", 18)

        cx, cy = self.W // 2, self.H // 2

        self._panel = Panel(
            pygame.Rect(cx - 320, cy - 200, 640, 400),
            font_title=self._font_title,
            font_body=self._font_med,
        )

        self._btn_back = Button(
            pygame.Rect(cx - 80, cy + 220, 160, 44),
            "RETOUR",
            self._font_small,
            colour=C_BTN,
            hover_colour=C_BTN_HOVER,
        )
        self._stats = None

    def on_enter(self) -> None:
        """Recharge les statistiques fraîches du joueur à l'ouverture de l'écran."""
        if self.app.current_user:
            self._stats = self.db.get_user_stats(self.app.current_user)
        else:
            self._stats = None

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._btn_back.handle_event(event):
            self.app.go_to("home")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.go_to("home")

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        self.screen.fill(C_BG)
        cx, cy = self.W // 2, self.H // 2

        # Dessin du conteneur central
        draw_rounded_rect(self.screen, C_PANEL, self._panel.rect, 16, border_colour=C_BORDER, border_width=2)

        # Titre de la page
        title_surf = self._font_title.render("COGNITIVE REVIEW", True, C_GOLD)
        blit_centered(self.screen, title_surf, cx, cy - 150)

        if not self.app.current_user:
            text = "NO USER CONNECTED"
            surf = self._font_med.render(text, True, C_WHITE)
            blit_centered(self.screen, surf, cx, cy)
        elif not self._stats:
            text = "NO DATA YET. FIRST PLAY!"
            surf = self._font_med.render(text, True, C_WHITE)
            blit_centered(self.screen, surf, cx, cy)
        else:
            total = self._stats['total_played']
            correct = self._stats['total_correct']
            ratio = (correct / total) * 100 if total > 0 else 0
            
            avg_time_correct = self._stats['avg_reaction_correct']
            avg_time_total = self._stats['avg_reaction_total']

            time_correct_str = f"{avg_time_correct:.0f} ms" if avg_time_correct else "N/A"
            time_total_str = f"{avg_time_total:.0f} ms" if avg_time_total else "N/A"

            # Liste des indicateurs à afficher à l'écran
            stats_lines = [
                f"CURRENT PLAYER : {self.app.current_user}",
                f"MUSIC TESTED : {total}",
                f"SUCCESS RATE : {correct} / {total} ({ratio:.1f}%)",
                f"REACTION TIME : {time_correct_str}",
                f"TOTAL REACTION TIME : {time_total_str}"
            ]

            y_pos = cy - 70
            for line in stats_lines:
                color = C_GOLD if "USER PROFILE" in line else C_WHITE
                surf = self._font_med.render(line, True, color)
                blit_centered(self.screen, surf, cx, y_pos)
                y_pos += 40

        self._btn_back.draw(self.screen)