import pygame
from src.constants import C_BG, C_GOLD, C_WHITE, C_BTN, C_BTN_HOVER

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

    def draw(self, screen):
        # Change de couleur si la souris survole
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)
    
class HomeScreen:
    def __init__(self, app):
        self.app = app
        # On crée un bouton au centre
        self.play_button = Button(
            app.width//2 - 100, app.height//2, 
            200, 60, "COMMENCER", 
            C_BTN, C_BTN_HOVER, C_WHITE
        )

    def on_enter(self): pass
    def on_exit(self): pass

    def handle_event(self, event):
        # Toujours possible de jouer avec Entrée
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.app.go_to("game")
        
        # Ou en cliquant sur le bouton
        if self.play_button.is_clicked(event):
            self.app.go_to("game")

    def update(self, dt): pass

    def draw(self):
        self.app.screen.fill(C_BG)
        
        # Titre
        font_title = pygame.font.SysFont("Arial", 50, bold=True)
        title = font_title.render("NEUROBEAT", True, C_GOLD)
        self.app.screen.blit(title, (self.app.width//2 - 140, 150))
        
        # Bouton
        self.play_button.draw(self.app.screen)