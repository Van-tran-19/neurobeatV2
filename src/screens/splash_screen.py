import pygame
from src.constants import C_BG, C_WHITE, SPLASH_DURATION

class SplashScreen:
    def __init__(self, app):
        self.app = app
        self.timer = 0

    def on_enter(self): self.timer = 0
    def on_exit(self): pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.app.go_to("home")

    def update(self, dt):
        self.timer += dt
        if self.timer >= SPLASH_DURATION:
            self.app.go_to("home")

    def draw(self):
        self.app.screen.fill(C_BG)
        # Ici, vous pourriez charger et afficher votre logo NeuroBeat
        font = pygame.font.SysFont("Arial", 64)
        text = font.render("NEUROBEAT", True, C_WHITE)
        self.app.screen.blit(text, (self.app.width//2 - 150, self.app.height//2 - 50))