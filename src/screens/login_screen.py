# src/screens/login_screen.py
import pygame
from src.screens.base_screen import BaseScreen
from src.constants import C_BG, C_GOLD, C_WHITE, C_BTN, C_BTN_HOVER, C_PANEL, C_BORDER
from src.widgets import Button, blit_centered, draw_rounded_rect

class LoginScreen(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._font_title = pygame.font.SysFont("Arial", 50, bold=True)
        self._font_label = pygame.font.SysFont("Arial", 24)
        self._font_input = pygame.font.SysFont("Arial", 32)
        
        self.username_input = ""
        self.input_active = True
        
        cx, cy = self.W // 2, self.H // 2
        
        self.input_rect = pygame.Rect(cx - 200, cy - 25, 400, 50)
        
        self._btn_login = Button(
            pygame.Rect(cx - 100, cy + 60, 200, 50),
            "LOGIN",
            self._font_label,
            colour=C_BTN,
            hover_colour=C_BTN_HOVER
        )

    def on_enter(self) -> None:
        self.username_input = ""

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._do_login()
            elif event.key == pygame.K_BACKSPACE:
                self.username_input = self.username_input[:-1]
            else:
                # Ajoute le caractère tapé
                self.username_input += event.unicode
                
        if self._btn_login.handle_event(event):
            self._do_login()

    def _do_login(self) -> None:
        if self.username_input.strip():
            self.app.login(self.username_input.strip())
            self.app.go_to("home")

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        self.screen.fill(C_BG)
        self._draw_dot_grid()

        cx, cy = self.W // 2, self.H // 2

        # Titre
        surf_title = self._font_title.render("LOGIN", True, C_GOLD)
        blit_centered(self.screen, surf_title, cx, 150)

        # Label
        surf_label = self._font_label.render("Enter your username :", True, C_WHITE)
        blit_centered(self.screen, surf_label, cx, cy - 60)

        # Champ de texte (fond)
        draw_rounded_rect(self.screen, C_PANEL, self.input_rect, 10, border_colour=C_BORDER, border_width=2)
        
        # Texte saisi
        surf_input = self._font_input.render(self.username_input, True, C_WHITE)
        # On centre le texte à l'intérieur du champ
        self.screen.blit(surf_input, (self.input_rect.x + 10, self.input_rect.y + 10))

        # Bouton
        self._btn_login.draw(self.screen)