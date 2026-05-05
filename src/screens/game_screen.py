"""
NeuroBeat — Game screen.
Lance la musique, gère le buzz (ESPACE), et déclenche la reconnaissance
vocale dans un thread séparé pour ne pas bloquer le rendu.
"""

from __future__ import annotations
import threading
import pygame

from src.screens.base_screen import BaseScreen
from src.constants import (
    C_BG, C_PANEL, C_BORDER, C_GOLD, C_WHITE, C_GREY,
    C_SUCCESS, C_FAIL, C_BTN, C_BTN_HOVER,
    PLAY_DURATION,
)
from src.widgets import (
    draw_rounded_rect, blit_centered,
    Panel, Button, ProgressBar, MusicStaff,
)


# États internes de l'écran de jeu
_STATE_PLAYING   = "playing"     # La musique tourne, on attend le buzz
_STATE_LISTENING = "listening"   # Le joueur parle
_STATE_RESULT    = "result"      # Affichage bon/mauvais
_STATE_NO_SONG   = "no_song"     # Base vide


class GameScreen(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)

        self._font_big   = pygame.font.SysFont("Arial", 42, bold=True)
        self._font_med   = pygame.font.SysFont("Arial", 26)
        self._font_small = pygame.font.SysFont("Arial", 18)

        cx, cy = self.W // 2, self.H // 2

        self._panel = Panel(
            pygame.Rect(cx - 320, cy - 160, 640, 320),
            font_title=self._font_big,
            font_body=self._font_med,
        )

        self._bar = ProgressBar(pygame.Rect(cx - 300, cy + 140, 600, 14))

        self._btn_home = Button(
            pygame.Rect(cx - 80, cy + 175, 160, 44),
            "ACCUEIL",
            self._font_small,
            colour=C_BTN,
            hover_colour=C_BTN_HOVER,
        )

        self._staff = MusicStaff(self.screen, 60, self.H - 55, self.W - 120, amplitude=20)

        # État runtime (réinitialisé dans on_enter)
        self._state        = _STATE_NO_SONG
        self._song         = None
        self._timer        = 0.0
        self._result_ok    = False
        self._guess        = ""
        self._stt_thread   = None
        self._result_timer = 0.0

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def on_enter(self) -> None:
        self._timer        = 0.0
        self._result_timer = 0.0
        self._guess        = ""

        last_song_id = getattr(self.app, 'last_song_id', None)

        self._song = self.db.get_random_song(
            theme=self.app.selected_theme, 
            exclude_id=last_song_id
        )

        if not self._song:
            self._state = _STATE_NO_SONG
            return

        self.app.last_song_id = self._song["id"]

        # Lance la musique
        try:
            pygame.mixer.music.load(self._song["filename"])
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[GameScreen] Impossible de charger l'audio : {e}")
            self._state = _STATE_NO_SONG
            return

        self._state = _STATE_PLAYING

    def on_exit(self) -> None:
        pygame.mixer.music.stop()
        # On laisse le thread STT se terminer proprement
        if self._stt_thread and self._stt_thread.is_alive():
            self._stt_thread.join(timeout=0)

    # ── Events ───────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._state == _STATE_PLAYING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._buzz()

        if self._state == _STATE_RESULT:
            if self._btn_home.handle_event(event):
                self.app.go_to("home")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.app.go_to("game")   # Rejouer

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._staff.update(dt)

        if self._state == _STATE_PLAYING:
            self._timer += dt
            self._bar.progress = max(0.0, 1.0 - self._timer / PLAY_DURATION)
            if self._timer >= PLAY_DURATION:
                # Temps écoulé → mauvaise réponse
                self._show_result(correct=False, guess="Time Over")

        elif self._state == _STATE_RESULT:
            self._result_timer += dt
            # Retour auto à l'accueil après 4 secondes
            if self._result_timer >= 4.0:
                self.app.go_to("Home")

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self) -> None:
        self.screen.fill(C_BG)
        self._draw_dot_grid()
        self._staff.draw()

        cx, cy = self.W // 2, self.H // 2
        
        # --- Affichage du profil utilisateur (HUD) ---
        if self.app.current_user:
            hud_text = f"Player: {self.app.current_user} | Score: {self.app.current_score}"
            surf_hud = self._font_small.render(hud_text, True, C_WHITE)
            self.screen.blit(surf_hud, (20, 20))

        if self._state == _STATE_NO_SONG:
            self._draw_no_song(cx, cy)

        if self._state == _STATE_NO_SONG:
            self._draw_no_song(cx, cy)

        elif self._state == _STATE_PLAYING:
            self._draw_playing(cx, cy)

        elif self._state == _STATE_LISTENING:
            self._draw_listening(cx, cy)

        elif self._state == _STATE_RESULT:
            self._draw_result(cx, cy)
            
    def _show_result(self, correct: bool, guess: str) -> None:
        pygame.mixer.music.stop()
        self._result_ok    = correct
        self._guess        = guess
        self._result_timer = 0.0
        self._state        = _STATE_RESULT

        # --- SEND SCORE TO DATABASE ---
        if correct and self.app.current_user:
            # 1. Add 100 points for a correct answer
            self.app.db.save_score(self.app.current_user, 100) 
            
            # 2. Fetch the newly updated profile
            profile = self.app.db.get_profile(self.app.current_user)
            if profile:
                # 3. Update the app's current score (MUST use the string key 'total_score')
                self.app.current_score = profile['total_score']

        # --- Sauvegarde du score si la réponse est correcte ---
        if correct and self.app.current_user:
            # On ajoute 100 points pour une bonne réponse (par exemple)
            self.app.db.save_score(self.app.current_user, 100) 
            # Mise à jour du score local dans l'app
            profile = self.app.db.get_profile(self.app.current_user)
            if profile:
               self.app.current_score = profile[2]

    # ── Private helpers ───────────────────────────────────────────────────────

    def _buzz(self) -> None:
        """Le joueur appuie sur ESPACE : on pause la musique et on écoute."""
        pygame.mixer.music.pause()
        self._state = _STATE_LISTENING
        expected    = self.engine.build_expected_words(self._song)
        self._stt_thread = threading.Thread(
            target=self._run_stt,
            args=(expected,),
            daemon=True,
        )
        self._stt_thread.start()

    def _run_stt(self, expected_words: list[str]) -> None:
        """Tourne dans un thread séparé pour ne pas geler le rendu."""
        guess = self.engine.recognize_speech(expected_words)
        correct = self.engine.check_answer(guess, self._song)
        # Retour dans le thread principal via un event pygame custom
        pygame.event.post(pygame.event.Event(
            pygame.USEREVENT,
            {"action": "stt_done", "guess": guess, "correct": correct},
        ))

    # On intercepte aussi les USEREVENT pour récupérer le résultat STT
    def handle_event(self, event: pygame.event.Event) -> None:  # noqa: F811
        if event.type == pygame.USEREVENT and getattr(event, "action", None) == "stt_done":
            self._show_result(event.correct, event.guess)
            return

        if self._state == _STATE_PLAYING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._buzz()

        if self._state == _STATE_RESULT:
            if self._btn_home.handle_event(event):
                self.app.go_to("home")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.app.go_to("game")

    # ── Draw sub-states ───────────────────────────────────────────────────────

    def _draw_playing(self, cx: int, cy: int) -> None:
        panel_r = self._panel.rect
        draw_rounded_rect(self.screen, C_PANEL, panel_r, 16,
                          border_colour=C_BORDER, border_width=2)

        hint = self._font_big.render("🎵  Listen Closely", True, C_WHITE)
        blit_centered(self.screen, hint, cx, cy - 50)

        sub = self._font_med.render("Press SPACE to buzz !", True, C_GREY)
        blit_centered(self.screen, sub, cx, cy + 20)

        self._bar.draw(self.screen)

    def _draw_listening(self, cx: int, cy: int) -> None:
        panel_r = self._panel.rect
        draw_rounded_rect(self.screen, C_PANEL, panel_r, 16,
                          border_colour=C_GOLD, border_width=3)

        lbl = self._font_big.render("🎤  SPEAK !", True, C_GOLD)
        blit_centered(self.screen, lbl, cx, cy - 50)

        sub = self._font_med.render("Say the artist or the title…", True, C_GREY)
        blit_centered(self.screen, sub, cx, cy + 20)

    def _draw_result(self, cx: int, cy: int) -> None:
        colour = C_SUCCESS if self._result_ok else C_FAIL
        panel_r = self._panel.rect
        draw_rounded_rect(self.screen, C_PANEL, panel_r, 16,
                          border_colour=colour, border_width=3)

        label = "✔  WELL DONEEEEEEEEE !" if self._result_ok else "✘  SHIET…"
        surf = self._font_big.render(label, True, colour)
        blit_centered(self.screen, surf, cx, cy - 80)

        # Réponse du joueur
        guess_lbl = self._font_small.render(f"You say : « {self._guess} »", True, C_GREY)
        blit_centered(self.screen, guess_lbl, cx, cy - 20)

        # La vraie réponse
        answer_str = f"{self._song['artist']}  —  {self._song['title']}"
        answer_surf = self._font_med.render(answer_str, True, C_WHITE)
        blit_centered(self.screen, answer_surf, cx, cy + 20)

        hint = self._font_small.render("Enter → play again   |   home button → menu", True, C_GREY)
        blit_centered(self.screen, hint, cx, cy + 70)

        self._btn_home.draw(self.screen)

    def _draw_no_song(self, cx: int, cy: int) -> None:
        panel_r = self._panel.rect
        draw_rounded_rect(self.screen, C_PANEL, panel_r, 16,
                          border_colour=C_FAIL, border_width=2)

        lbl = self._font_big.render("Any song available", True, C_FAIL)
        blit_centered(self.screen, lbl, cx, cy - 30)

        sub = self._font_med.render("Add songs with tests/init_data.py", True, C_GREY)
        blit_centered(self.screen, sub, cx, cy + 30)

        self._btn_home.draw(self.screen)
