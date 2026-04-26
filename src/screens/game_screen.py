import pygame
from src.constants import C_BG, C_WHITE, C_GOLD, C_PANEL
from src.engine.stt_live import live_transcribe_optimized
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "vosk-model-small-fr-0.22")

class GameScreen:
    def __init__(self, app):
        self.app = app
        self.current_song = None
        self.is_listening = False

    def on_enter(self):
        self.current_song = self.app.db.get_random_song()
        if not self.current_song:
            self.app.go_to("home")
            return
            
        pygame.mixer.music.load(self.current_song['filename'])
        pygame.mixer.music.play()
        self.is_listening = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.is_listening:
                pygame.mixer.music.pause()
                self.is_listening = False
                self.check_answer()

    def check_answer(self):
        # On lance la reconnaissance vocale
        # Remarque : MODEL_PATH doit être défini ou importé
        guess = live_transcribe_optimized(MODEL_PATH)
        print(f"Vous avez dit : {guess}")
        
        # Logique de validation simplifiée
        if guess.lower() in self.current_song['phonetic_answers'].lower():
            print("BRAVO !")
        else:
            print("DOMMAGE...")
        self.app.go_to("home")

    def update(self, dt): pass

    def draw(self):
        self.app.screen.fill(C_BG)
        font = pygame.font.SysFont("Arial", 30)

        # Panneau central
        panel_rect = pygame.Rect(self.app.width//4, self.app.height//4, self.app.width//2, self.app.height//2)
        pygame.draw.rect(self.app.screen, C_PANEL, panel_rect, border_radius=20)
        
        if self.is_listening:
            txt = "ÉCOUTEZ BIEN..."
            sub_txt = "Appuyez sur ESPACE pour buzzer !"
            color = C_WHITE
        else:
            txt = "ANALYSE DE VOTRE VOIX..."
            sub_txt = "Parlez maintenant !"
            color = C_GOLD

        # Affichage des textes
        surf = font.render(txt, True, color)
        self.app.screen.blit(surf, (self.app.width//2 - surf.get_width()//2, self.app.height//2 - 50))
        
        sub_surf = font.render(sub_txt, True, C_WHITE)
        self.app.screen.blit(sub_surf, (self.app.width//2 - sub_surf.get_width()//2, self.app.height//2 + 20))