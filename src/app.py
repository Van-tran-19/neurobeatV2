"""
NeuroBeat — Application controller.

Owns the pygame window, the clock, the database instance, the GameEngine,
and the screen registry. All screen navigation goes through `app.go_to(key)`.
"""
from __future__ import annotations

import sys
import os
import pygame
from src.constants import WIDTH, HEIGHT, FPS
from data.database import DatabaseManager
from src.game_logic import GameEngine
from src.screens.splash_screen import SplashScreen
from src.screens.home_screen import HomeScreen
from src.screens.game_screen import GameScreen
from src.screens.login_screen import LoginScreen
from src.screens.leaderboard_screen import LeaderboardScreen
from src.screens.stats_screen import StatsScreen
AUDIO_PATH = os.path.join(sys.path[0], "assets", "audio")

class App:
    def __init__(self) -> None:
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("NeuroBeat")
        pygame.mouse.set_visible(True)
        self.clock  = pygame.time.Clock()
        self.width  = WIDTH
        self.height = HEIGHT

        # Couche données
        self.db: DatabaseManager = DatabaseManager()
        self.current_user = None
        self.current_score = 0
        self.session_id = None

        # Moteur de jeu (STT + validation) partagé entre tous les screens
        # Moteur de jeu (STT + validation) partagé entre tous les screens
        # On lui passe self.db pour qu'il puisse lire les données
        self.engine: GameEngine = GameEngine(self.db)

        # Thème sélectionné sur le home screen (None = tous les thèmes)
        self.selected_theme: str | None = None

        # Registre des écrans — instanciés une seule fois
        self._screens: dict[str, object] = {
            "splash": SplashScreen(self),
            "login":  LoginScreen(self),
            "home":   HomeScreen(self),
            "game":   GameScreen(self),
            "leaderboard": LeaderboardScreen(self),
            "stats":  StatsScreen(self),
        }

        # Démarrage directement sur le home screen au lieu du splash/login
        self._active_key: str = "home"
        self._active          = self._screens["home"]
        self._active.on_enter()

        # --- Mode 1v1 (Blind Test) ---
        self.mode_1v1 = False         # False = Solo, True = 1v1
        self.nom_j1 = "Joueur 1"
        self.nom_j2 = "Joueur 2"
        self.score_j1 = 0
        self.score_j2 = 0
        self.buzzer_actif = None       # Contiendra 'J1' ou 'J2' pendant la reconnaissance vocale

        self.nb_manches_totales = 3   
        self.manches_jouees = 0


    def go_to(self, key: str) -> None:
        """Navigue vers un écran nommé."""
        if key not in self._screens:
            raise KeyError(f"Unknown screen: '{key}'")
        self._active.on_exit()
        self._active_key = key
        self._active     = self._screens[key]
        self._active.on_enter()
        
    def login(self, name: str) -> None:
        """Connecte l'utilisateur et récupère son score."""
        self.current_user = name
        
        # 1. On nettoie la base de données des éventuels doublons AVANT de charger
        self.db.clean_duplicate_profiles()
        
        # 2. On récupère le profil (qui est maintenant garanti d'être unique)
        profile = self.db.get_profile(name)
        
        if profile:
            self.current_score = profile['total_score']
        else:
            self.current_score = 0
            self.db.save_score(name, 0) # Crée le nouvel utilisateur s'il n'existe pas
            
        print(f"Logged in as: {self.current_user} | Score: {self.current_score}")

    def run(self) -> None:
        pygame.mouse.set_visible(False) # On cache la vraie souris défectueuse
        
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                self._active.handle_event(event)

            self._active.update(dt)
            self._active.draw()
            
            # --- DESSINE UNE SOURIS MANUELLE ---
            mx, my = pygame.mouse.get_pos()
            pygame.draw.circle(self.screen, (255, 255, 255), (mx, my), 5) # Un petit point blanc
            pygame.draw.circle(self.screen, (0, 0, 0), (mx, my), 5, 1)    # Un contour noir
            
            pygame.display.flip()
