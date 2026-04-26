import pygame
from src.constants import C_BG, C_GOLD, C_WHITE

class HomeScreen:
    def __init__(self, app):
        self.app = app

    def on_enter(self): pass
    def on_exit(self): pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN: # Appuyez sur Entrée pour jouer
                self.app.go_to("game")

    def update(self, dt): pass

    def draw(self):
        self.app.screen.fill(C_BG)
        font = pygame.font.SysFont("Arial", 32)
        label = font.render("Appuyez sur ENTRÉE pour commencer", True, C_GOLD)
        self.app.screen.blit(label, (self.app.width//2 - 250, self.app.height//2))