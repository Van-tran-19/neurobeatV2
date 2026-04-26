import pygame
from src.constants import C_BG, C_WHITE, PLAY_DURATION
from src.engine.stt_live import live_transcribe_optimized
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "vosk-model-small-fr-0.22")

class GameScreen:
    def __init__(self, app):
        self.app = app
        self.current_song = None

    def on_enter(self):
        # On récupère une musique au hasard
        self.current_song = self.app.db.get_random_song()
        pygame.mixer.music.load(self.current_song['filename'])
        pygame.mixer.music.play()
        print(f"En écoute : {self.current_song['title']}")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: # Simule le buzzer
                pygame.mixer.music.pause()
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
        # Affichage d'un disque ou d'une animation