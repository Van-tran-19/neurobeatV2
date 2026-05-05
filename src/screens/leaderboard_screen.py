# src/screens/leaderboard_screen.py
from __future__ import annotations
import pygame

from src.screens.base_screen import BaseScreen
from src.constants import C_BG, C_GOLD, C_WHITE, C_PANEL, C_BORDER, C_BTN, C_BTN_HOVER, C_GREY, C_SUCCESS
from src.widgets import Button, blit_centered, draw_rounded_rect

class LeaderboardScreen(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._font_title  = pygame.font.SysFont("Arial", 50, bold=True)
        self._font_header = pygame.font.SysFont("Arial", 28, bold=True)
        self._font_row    = pygame.font.SysFont("Arial", 24)
        
        cx = self.W // 2
        
        self._btn_back = Button(
            pygame.Rect(cx - 100, self.H - 90, 200, 50),
            "BACK",
            self._font_header,
            colour=C_BTN,
            hover_colour=C_BTN_HOVER
        )
        self.display_players = []

    def on_enter(self) -> None:
        """Fetch players and ensure the current player is always visible."""
        # 1. Get ALL players ordered by score
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username, total_score FROM profiles ORDER BY total_score DESC')
            all_players = [dict(row) for row in cursor.fetchall()]

        self.display_players = []
        current_found = False

        # 2. Build the display list
        for i, p in enumerate(all_players):
            p_data = {
                'rank': i + 1, 
                'username': p['username'], 
                'score': p['total_score']
            }
            
            # Keep the top 5 players
            if i < 5:
                self.display_players.append(p_data)
                if p['username'] == self.app.current_user:
                    current_found = True
            
            # If we are past the top 5, only look for the current player
            else:
                if p['username'] == self.app.current_user and not current_found:
                    # If there's a gap between rank 5 and the current player, add "..."
                    if i > 5:
                        self.display_players.append({
                            'rank': '...', 
                            'username': '...', 
                            'score': '...'
                        })
                    
                    self.display_players.append(p_data)
                    break # Stop searching once we found the current player

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        # Go back if the user clicks the button or presses ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.go_to("home")
            
        if self._btn_back.handle_event(event):
            self.app.go_to("home")

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        self.screen.fill(C_BG)
        self._draw_dot_grid()

        cx = self.W // 2
        
        # Title
        title_surf = self._font_title.render("LEADERBOARD", True, C_GOLD)
        blit_centered(self.screen, title_surf, cx, 60)

        # Background Panel for the table
        panel_rect = pygame.Rect(cx - 320, 130, 640, 460)
        draw_rounded_rect(self.screen, C_PANEL, panel_rect, 15, border_colour=C_BORDER, border_width=2)

        # Table Headers
        y_offset = 150
        self.screen.blit(self._font_header.render("Rank", True, C_GOLD), (cx - 260, y_offset))
        self.screen.blit(self._font_header.render("Player", True, C_GOLD), (cx - 100, y_offset))
        self.screen.blit(self._font_header.render("Score", True, C_GOLD), (cx + 170, y_offset))
        
        # Separator line
        pygame.draw.line(self.screen, C_BORDER, (cx - 290, y_offset + 40), (cx + 290, y_offset + 40), 2)

        # Draw the players
        y_offset += 60
        for p in self.display_players:
            
            # Color logic: Green for current player, Gold for 1st, Grey for "...", White for rest
            if p['username'] == self.app.current_user:
                color = C_SUCCESS
            elif p['rank'] == 1:
                color = C_GOLD
            elif p['rank'] == '...':
                color = C_GREY
            else:
                color = C_WHITE 
            
            rank_surf  = self._font_row.render(str(p['rank']), True, color)
            name_surf  = self._font_row.render(p['username'], True, color)
            score_surf = self._font_row.render(str(p['score']), True, color)
            
            self.screen.blit(rank_surf, (cx - 250, y_offset))
            self.screen.blit(name_surf, (cx - 100, y_offset))
            self.screen.blit(score_surf, (cx + 170, y_offset))
            
            y_offset += 55

        # If database is entirely empty
        if not self.display_players:
            empty_surf = self._font_row.render("No scores recorded yet.", True, C_GREY)
            blit_centered(self.screen, empty_surf, cx, 300)

        # Back Button
        self._btn_back.draw(self.screen)