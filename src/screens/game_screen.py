# game_screen.py
"""
NeuroBeat — Game screen.
Starts the music, handles the buzz (SPACE), and triggers voice recognition
in a separate thread to avoid blocking the render.
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


# Internal states of the game screen
_STATE_PLAYING   = "playing"     # Music is playing, waiting for the buzz
_STATE_LISTENING = "listening"   # The player is speaking
_STATE_RESULT    = "result"      # Display good/bad result
_STATE_NO_SONG   = "no_song"     # Empty database


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
            "HOME",
            self._font_small,
            colour=C_BTN,
            hover_colour=C_BTN_HOVER,
        )

        self._staff = MusicStaff(self.screen, 60, self.H - 55, self.W - 120, amplitude=20)

        # Runtime state (reset in on_enter)
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

        # Starts the music
        try:
            pygame.mixer.music.load(self._song["filename"])
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[GameScreen] Unable to load audio: {e}")
            self._state = _STATE_NO_SONG
            return

        self._state = _STATE_PLAYING

    def on_exit(self) -> None:
        pygame.mixer.music.stop()
        # Let the STT thread finish properly
        if self._stt_thread and self._stt_thread.is_alive():
            self._stt_thread.join(timeout=0)

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._staff.update(dt)

        if self._state == _STATE_PLAYING:
            self._timer += dt
            self._bar.progress = max(0.0, 1.0 - self._timer / PLAY_DURATION)
            if self._timer >= PLAY_DURATION:
                # Time elapsed → wrong answer
                self._show_result(correct=False, guess="Time Over")

        elif self._state == _STATE_RESULT:
            self._result_timer += dt
            # Auto return to home after 4 seconds
            if self._result_timer >= 5.0:
                self._next_round_or_home()

    # ── Draw 

    def draw(self) -> None:
        self.screen.fill(C_BG)
        self._draw_dot_grid()
        self._staff.draw()

        cx, cy = self.W // 2, self.H // 2
        
        # --- Display user profile (HUD) ---
        # --- Display user profile / 1v1 HUD ---
        if self.app.mode_1v1:
            manche_actuelle = min(self.app.manches_jouees + 1, self.app.nb_manches_totales)
            manche_str = f"Round {manche_actuelle} / {self.app.nb_manches_totales}"
            
            if self.app.manches_jouees >= self.app.nb_manches_totales:
                manche_str = "Sudden Death (Draw)"

            hud_text = f"🎮 {self.app.nom_j1}: {self.app.score_j1} pts   VS   {self.app.nom_j2}: {self.app.score_j2} pts  |  {manche_str}"
            
            color = C_WHITE
            # Visual tie indicator if the score is not 0-0
            if self.app.score_j1 == self.app.score_j2 and self.app.score_j1 > 0:
                hud_text += "  [🔥 Draw]"
                color = C_GOLD
                
            surf_hud = self._font_small.render(hud_text, True, color)
            self.screen.blit(surf_hud, (20, 20))

        elif self.app.current_user:
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

        if self.app.mode_1v1:
            self.app.manches_jouees += 1

        if correct:
            if self.app.mode_1v1:
                if self.app.buzzer_actif == "J1":
                    self.app.score_j1 += 100
                elif self.app.buzzer_actif == "J2":
                    self.app.score_j2 += 100
            elif self.app.current_user:
                # Existing code for solo mode / DB
                self.app.db.save_score(self.app.current_user, 100) 
                profile = self.app.db.get_profile(self.app.current_user)
                if profile:
                    self.app.current_score = profile['total_score']

        # --- SEND SCORE TO DATABASE ---
        if correct and self.app.current_user:
            # 1. Add 100 points for a correct answer
            self.app.db.save_score(self.app.current_user, 100) 
            
            # 2. Fetch the newly updated profile
            profile = self.app.db.get_profile(self.app.current_user)
            if profile:
                # 3. Update the app's current score (MUST use the string key 'total_score')
                self.app.current_score = profile['total_score']

        # --- Saving the score if the answer is correct ---
        if correct and self.app.current_user:
            # Add 100 points for a correct answer (for example)
            self.app.db.save_score(self.app.current_user, 100) 
            # Update local score in the app
            profile = self.app.db.get_profile(self.app.current_user)
            if profile:
               self.app.current_score = profile[2]
               
        # --- COGNITIVE LOG RECORDING ---
        if self.app.session_id and self._song:
            reaction_ms = self._timer * 1000.0
            self.app.db.log_reaction(
                session_id=self.app.session_id,
                song_id=self._song["id"],
                reaction_time_ms=reaction_ms,
                was_correct=correct
            )

        # --- SEND SCORE TO THE DATABASE ---
        if correct and self.app.current_user:
            self.app.db.save_score(self.app.current_user, 100) 
            profile = self.app.db.get_profile(self.app.current_user)
            if profile:
                self.app.current_score = profile['total_score']

    # ── Private helpers 

    def _buzz(self) -> None:
        """The player presses SPACE: pause the music and listen."""
        pygame.mixer.music.pause()
        self._state = _STATE_LISTENING
        
        # Pass the entire song directly to the thread
        self._stt_thread = threading.Thread(
            target=self._run_stt,
            args=(self._song,),
            daemon=True,
        )
        self._stt_thread.start()

    def _run_stt(self, song_data: dict) -> None: 
        """Runs in a separate thread to avoid freezing the render."""
        # The GameEngine now handles language choice internally
        guess = self.engine.recognize_speech(song_data)
        correct = self.engine.check_answer(guess, song_data)
        
        pygame.event.post(pygame.event.Event(
            pygame.USEREVENT,
            {"action": "stt_done", "guess": guess, "correct": correct},
        ))

    # Also intercept USEREVENT to get the STT result
    # Also intercept USEREVENT to get the STT result
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.USEREVENT and getattr(event, "action", None) == "stt_done":
            self._show_result(event.correct, event.guess)
            return

        if self._state == _STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if self.app.mode_1v1:
                    # --- 1v1 MODE: Keys S (Player 1) and L (Player 2) ---
                    if event.key == pygame.K_s:
                        self.app.buzzer_actif = "J1"
                        self._buzz()
                    elif event.key == pygame.K_l:
                        self.app.buzzer_actif = "J2"
                        self._buzz()
                else:
                    # --- SOLO MODE: Space Bar ---
                    if event.key == pygame.K_SPACE:
                        self._buzz()

        if self._state == _STATE_RESULT:
            if self._btn_home.handle_event(event):
                self.app.go_to("home")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._next_round_or_home()
        
        if self._state == _STATE_NO_SONG:
            if self._btn_home.handle_event(event):
                self.app.go_to("home")
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN):
                self.app.go_to("home")

    # ── Draw sub-states 

    def _draw_playing(self, cx: int, cy: int) -> None:
        panel_r = self._panel.rect
        draw_rounded_rect(self.screen, C_PANEL, panel_r, 16, border_colour=C_BORDER, border_width=2)

        hint = self._font_big.render("🎵  Listen Closely", True, C_WHITE)
        blit_centered(self.screen, hint, cx, cy - 50)

        if self.app.mode_1v1:
            msg = f"{self.app.nom_j1} [S]  |  [L] {self.app.nom_j2} — BUZZER !"
        else:
            msg = "Press SPACE to buzz !"
            
        sub = self._font_med.render(msg, True, C_GREY)
        blit_centered(self.screen, sub, cx, cy + 20)
        self._bar.draw(self.screen)

    def _draw_listening(self, cx: int, cy: int) -> None:
        panel_r = self._panel.rect
        draw_rounded_rect(self.screen, C_PANEL, panel_r, 16, border_colour=C_GOLD, border_width=3)

        nom_joueur = self.app.nom_j1 if self.app.buzzer_actif == "J1" else self.app.nom_j2
        lbl = self._font_big.render(f"🎤 {nom_joueur.upper()} SPEAK !", True, C_GOLD)
        blit_centered(self.screen, lbl, cx, cy - 50)

        sub = self._font_med.render("Say the artist or the title…", True, C_GREY)
        blit_centered(self.screen, sub, cx, cy + 20)

    def _draw_result(self, cx: int, cy: int) -> None:
        colour = C_SUCCESS if self._result_ok else C_FAIL
        panel_r = self._panel.rect
        draw_rounded_rect(self.screen, C_PANEL, panel_r, 16,
                          border_colour=colour, border_width=3)

        label = "✔  WELL DONEEEEEEEEE !" if self._result_ok else "✘  TIME OVER "
        surf = self._font_big.render(label, True, colour)
        blit_centered(self.screen, surf, cx, cy - 80)

        # Player's answer
        guess_lbl = self._font_small.render(f"You say : « {self._guess} »", True, C_GREY)
        blit_centered(self.screen, guess_lbl, cx, cy - 30)

        # The real answer
        answer_str = f"{self._song['artist']}  —  {self._song['title']}"
        answer_surf = self._font_med.render(answer_str, True, C_WHITE)
        blit_centered(self.screen, answer_surf, cx, cy + 10)

        # Use .get() to avoid a crash if the anecdote is missing
        anecdote_text = self._song.get('anecdote', "")
        if not anecdote_text:
            anecdote_text = "No fun fact available"
            
        # The panel is 640px wide, limit text to 580px to keep a margin
        max_width = 580 
        words = anecdote_text.split(' ')
        lines = []
        current_line = ""

        # Splitting text into multiple lines
        for word in words:
            test_line = current_line + word + " "
            # self._font_med.size(text)[0] returns the text width in pixels
            if self._font_med.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line) # Don't forget to add the very last line

        # Display line by line
        y_offset = cy + 55  # Starting position for the anecdote
        for line in lines:
            line_surf = self._font_med.render(line.strip(), True, C_GOLD)
            blit_centered(self.screen, line_surf, cx, y_offset)
            y_offset += 28  # Move down by 28 pixels for each new line

        # Position the hint dynamically below the last line
        hint = self._font_small.render("Enter → play again   |   home button → menu", True, C_GREY)
        blit_centered(self.screen, hint, cx, y_offset + 20)

        self._btn_home.draw(self.screen)

    def _draw_no_song(self, cx: int, cy: int) -> None:
        panel_r = self._panel.rect
        draw_rounded_rect(self.screen, C_PANEL, panel_r, 16,
                          border_colour=C_FAIL, border_width=2)

        lbl = self._font_big.render("Any song available", True, C_FAIL)
        blit_centered(self.screen, lbl, cx, cy - 30)

        sub = self._font_med.render("Ask us if you want any other songs", True, C_GREY)
        blit_centered(self.screen, sub, cx, cy + 30)

        self._btn_home.draw(self.screen)
    
    def _next_round_or_home(self) -> None:
        """Determines whether to start the next round, apply sudden death, or finish."""
        if self.app.mode_1v1:
            if self.app.manches_jouees >= self.app.nb_manches_totales:
                if self.app.score_j1 == self.app.score_j2:
                    # TIE: Sudden death (add 1 round)
                    self.app.nb_manches_totales += 1
                    self.app.go_to("game")
                else:
                    # END: Someone won, return to main menu
                    self.app.go_to("home")
            else:
                self.app.go_to("game")
        else:
            self.app.go_to("home")