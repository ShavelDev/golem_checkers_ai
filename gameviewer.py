#!/usr/bin/env python3
"""
Pygame-based visualizer for checkers training games.
Shows games move-by-move with playback controls.
"""

import pygame
import pickle
import os
import sys


class GameVisualizer:
    """Visualize checkers games using pygame."""
    
    # Colors
    DARK_SQUARE = (139, 69, 19)  # Dark brown
    LIGHT_SQUARE = (245, 222, 179)  # Wheat
    BACKGROUND = (50, 50, 50)  # Dark gray
    TEXT_COLOR = (255, 255, 255)  # White
    BUTTON_COLOR = (70, 130, 180)  # Steel blue
    BUTTON_HOVER = (100, 160, 210)  # Light steel blue
    
    # Piece colors
    PLAYER_PIECE = (220, 20, 60)  # Crimson red
    PLAYER_KING = (139, 0, 0)  # Dark red
    OPPONENT_PIECE = (255, 255, 255)  # White
    OPPONENT_KING = (200, 200, 200)  # Light gray
    KING_CROWN = (255, 215, 0)  # Gold
    
    def __init__(self, games_dir="training_games", square_size=70):
        """
        Initialize the visualizer.
        
        Args:
            games_dir: Directory containing game pickle files
            square_size: Size of each board square in pixels
        """
        self.games_dir = games_dir
        self.square_size = square_size
        self.board_size = 8 * square_size
        
        # Window dimensions
        self.info_panel_width = 350
        self.window_width = self.board_size + self.info_panel_width
        self.window_height = self.board_size + 100  # Extra space for controls
        
        # Game state
        self.games = []
        self.current_game_idx = 0
        self.current_move_idx = 0
        self.playing = False
        self.playback_speed = 1.0  # Moves per second
        self.last_update_time = 0
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Checkers Game Visualizer")
        self.clock = pygame.time.Clock()
        
        # Load games
        self.load_games()
    
    def draw_text_simple(self, text, x, y, size='medium', color=None):
        """
        Draw text using simple colored rectangles (no fonts needed).
        Only supports numbers and basic info display.
        """
        if color is None:
            color = self.TEXT_COLOR
        
        # Simple visual indicators instead of text
        # Just draw colored rectangles to show information presence
        if size == 'large':
            height = 8
            width = 120
        elif size == 'medium':
            height = 6
            width = 100
        else:  # small
            height = 4
            width = 80
        
        pygame.draw.rect(self.screen, color, (x, y, width, height), 1)
        
    def load_games(self):
        """Load all game files from directory."""
        self.games = []
        
        if not os.path.exists(self.games_dir):
            print(f"Directory {self.games_dir} not found!")
            return
        
        for filename in sorted(os.listdir(self.games_dir)):
            if filename.endswith('.pkl'):
                filepath = os.path.join(self.games_dir, filename)
                try:
                    with open(filepath, 'rb') as f:
                        game = pickle.load(f)
                        self.games.append(game)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        print(f"Loaded {len(self.games)} games")
    
    def get_current_game(self):
        """Get the currently displayed game."""
        if not self.games:
            return None
        return self.games[self.current_game_idx]
    
    def get_current_board(self):
        """Get the board at the current move."""
        game = self.get_current_game()
        if not game:
            return None
        
        if self.current_move_idx == 0:
            # Initial board - reconstruct from first move
            if game['move_history']:
                return game['move_history'][0]['board_before_8x8']
            return None
        elif self.current_move_idx <= len(game['move_history']):
            return game['move_history'][self.current_move_idx - 1]['board_after_8x8']
        
        return game['final_board']
    
    def draw_board(self):
        """Draw the checkers board with pieces."""
        board = self.get_current_board()
        if not board:
            return
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x = col * self.square_size
                y = row * self.square_size
                
                # Checkerboard pattern
                if (row + col) % 2 == 0:
                    color = self.LIGHT_SQUARE
                else:
                    color = self.DARK_SQUARE
                
                pygame.draw.rect(self.screen, color, 
                               (x, y, self.square_size, self.square_size))
        
        # Draw pieces
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != 0:
                    self.draw_piece(row, col, piece)
        
        # Draw grid lines
        for i in range(9):
            # Vertical lines
            pygame.draw.line(self.screen, (0, 0, 0),
                           (i * self.square_size, 0),
                           (i * self.square_size, self.board_size), 1)
            # Horizontal lines
            pygame.draw.line(self.screen, (0, 0, 0),
                           (0, i * self.square_size),
                           (self.board_size, i * self.square_size), 1)
    
    def draw_piece(self, row, col, piece):
        """Draw a single piece."""
        center_x = col * self.square_size + self.square_size // 2
        center_y = row * self.square_size + self.square_size // 2
        radius = self.square_size // 3
        
        # Determine piece color
        if piece > 0:  # Player pieces (1 or 2)
            if abs(piece) == 2:
                color = self.PLAYER_KING
            else:
                color = self.PLAYER_PIECE
        else:  # Opponent pieces (-1 or -2)
            if abs(piece) == 2:
                color = self.OPPONENT_KING
            else:
                color = self.OPPONENT_PIECE
        
        # Draw piece
        pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, (0, 0, 0), (center_x, center_y), radius, 2)
        
        # Draw crown for kings
        if abs(piece) == 2:
            self.draw_crown(center_x, center_y, radius)
    
    def draw_crown(self, x, y, radius):
        """Draw a crown on a king piece."""
        crown_size = radius // 2
        points = [
            (x - crown_size, y),
            (x - crown_size//2, y - crown_size//2),
            (x, y),
            (x + crown_size//2, y - crown_size//2),
            (x + crown_size, y)
        ]
        pygame.draw.lines(self.screen, self.KING_CROWN, False, points, 3)
    
    def draw_info_panel(self):
        """Draw the information panel on the right side using visual indicators."""
        panel_x = self.board_size
        panel_y = 0
        
        # Background
        pygame.draw.rect(self.screen, self.BACKGROUND,
                        (panel_x, panel_y, self.info_panel_width, self.window_height))
        
        game = self.get_current_game()
        if not game:
            # Draw indicator for no games
            pygame.draw.circle(self.screen, (255, 0, 0), 
                             (panel_x + 100, 100), 30, 3)
            return
        
        y_offset = 20
        x_offset = panel_x + 20
        
        # Game info section - visual indicators
        # Title area
        pygame.draw.rect(self.screen, self.TEXT_COLOR, 
                        (x_offset, y_offset, 200, 3))
        y_offset += 20
        
        # Game number indicator (small circles)
        for i in range(min(10, len(self.games))):
            color = (0, 255, 0) if i == self.current_game_idx else (100, 100, 100)
            pygame.draw.circle(self.screen, color, 
                             (x_offset + i * 20, y_offset + 5), 5)
        y_offset += 30
        
        # Depth indicators (bars)
        # Strong bot depth
        strong_width = game['player1_depth'] * 30
        pygame.draw.rect(self.screen, (255, 100, 100), 
                        (x_offset, y_offset, strong_width, 15))
        y_offset += 20
        
        # Weak bot depth
        weak_width = game['player2_depth'] * 30
        pygame.draw.rect(self.screen, (100, 100, 255), 
                        (x_offset, y_offset, weak_width, 15))
        y_offset += 30
        
        # Winner indicator
        if game['winner'] == 1:
            winner_color = (255, 100, 100)  # Red for strong
        elif game['winner'] == -1:
            winner_color = (100, 100, 255)  # Blue for weak
        else:
            winner_color = (150, 150, 150)  # Gray for draw
        pygame.draw.circle(self.screen, winner_color, 
                         (x_offset + 50, y_offset + 15), 20)
        y_offset += 50
        
        # Move progress bar
        progress = self.current_move_idx / max(game['total_moves'], 1)
        bar_width = 250
        bar_height = 20
        
        # Background bar
        pygame.draw.rect(self.screen, (80, 80, 80), 
                        (x_offset, y_offset, bar_width, bar_height))
        # Progress bar
        pygame.draw.rect(self.screen, (0, 255, 0), 
                        (x_offset, y_offset, int(bar_width * progress), bar_height))
        # Border
        pygame.draw.rect(self.screen, self.TEXT_COLOR, 
                        (x_offset, y_offset, bar_width, bar_height), 2)
        y_offset += 40
        
        # Current move details
        if self.current_move_idx > 0 and self.current_move_idx <= len(game['move_history']):
            move = game['move_history'][self.current_move_idx - 1]
            
            y_offset += 10
            # Section divider
            pygame.draw.rect(self.screen, self.TEXT_COLOR, 
                            (x_offset, y_offset, 200, 3))
            y_offset += 20
            
            # Player indicator
            player_color = (255, 100, 100) if move['player'] == 1 else (100, 100, 255)
            pygame.draw.circle(self.screen, player_color, 
                             (x_offset + 30, y_offset + 10), 15)
            
            # Move type indicator (R for random, M for minimax)
            move_type = move.get('move_type', 'minimax')
            if move_type == 'random':
                # Draw 'R' shape using lines (random move)
                pygame.draw.line(self.screen, (255, 255, 0), 
                               (x_offset + 80, y_offset), (x_offset + 80, y_offset + 20), 3)
                pygame.draw.line(self.screen, (255, 255, 0), 
                               (x_offset + 80, y_offset), (x_offset + 90, y_offset), 3)
                pygame.draw.line(self.screen, (255, 255, 0), 
                               (x_offset + 90, y_offset), (x_offset + 90, y_offset + 10), 3)
                pygame.draw.line(self.screen, (255, 255, 0), 
                               (x_offset + 90, y_offset + 10), (x_offset + 80, y_offset + 10), 3)
                pygame.draw.line(self.screen, (255, 255, 0), 
                               (x_offset + 80, y_offset + 10), (x_offset + 90, y_offset + 20), 3)
            else:
                # Draw 'M' shape using lines (minimax move)
                pygame.draw.line(self.screen, (0, 255, 255), 
                               (x_offset + 80, y_offset + 20), (x_offset + 80, y_offset), 3)
                pygame.draw.line(self.screen, (0, 255, 255), 
                               (x_offset + 80, y_offset), (x_offset + 85, y_offset + 10), 3)
                pygame.draw.line(self.screen, (0, 255, 255), 
                               (x_offset + 85, y_offset + 10), (x_offset + 90, y_offset), 3)
                pygame.draw.line(self.screen, (0, 255, 255), 
                               (x_offset + 90, y_offset), (x_offset + 90, y_offset + 20), 3)
            
            y_offset += 40
            
            # Board value indicator (horizontal bar, centered at 0)
            value = move['board_value']
            max_value = 20
            normalized = max(-1, min(1, value / max_value))
            
            center_x = x_offset + 125
            if normalized > 0:
                # Positive value (good for player)
                bar_len = int(normalized * 100)
                pygame.draw.rect(self.screen, (0, 255, 0), 
                               (center_x, y_offset, bar_len, 15))
            else:
                # Negative value (bad for player)
                bar_len = int(-normalized * 100)
                pygame.draw.rect(self.screen, (255, 0, 0), 
                               (center_x - bar_len, y_offset, bar_len, 15))
            
            # Center line
            pygame.draw.line(self.screen, self.TEXT_COLOR, 
                           (center_x, y_offset - 5), (center_x, y_offset + 20), 2)
    
    def draw_controls(self):
        """Draw playback controls at the bottom using visual indicators."""
        control_y = self.board_size + 10
        
        # Background
        pygame.draw.rect(self.screen, self.BACKGROUND,
                        (0, self.board_size, self.window_width, 100))
        
        # Buttons with symbols instead of text
        button_width = 80
        button_height = 30
        button_y = control_y + 10
        spacing = 10
        start_x = 20
        
        buttons = [
            ("<<", self.prev_game),
            ("<", self.prev_move),
            ("||" if self.playing else ">", self.toggle_play),
            (">", self.next_move),
            (">>", self.next_game),
        ]
        
        self.buttons = []
        x = start_x
        
        for symbol, callback in buttons:
            button_rect = pygame.Rect(x, button_y, button_width, button_height)
            self.buttons.append((button_rect, callback, symbol))
            
            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            color = self.BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
            
            pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.TEXT_COLOR, button_rect, 2, border_radius=5)
            
            # Draw simple symbols
            center_x = button_rect.centerx
            center_y = button_rect.centery
            
            if symbol == "<<":
                # Double left arrows
                points1 = [(center_x - 10, center_y), (center_x - 20, center_y - 8), (center_x - 20, center_y + 8)]
                points2 = [(center_x + 5, center_y), (center_x - 5, center_y - 8), (center_x - 5, center_y + 8)]
                pygame.draw.polygon(self.screen, self.TEXT_COLOR, points1)
                pygame.draw.polygon(self.screen, self.TEXT_COLOR, points2)
            elif symbol == "<":
                # Single left arrow
                points = [(center_x + 5, center_y), (center_x - 8, center_y - 10), (center_x - 8, center_y + 10)]
                pygame.draw.polygon(self.screen, self.TEXT_COLOR, points)
            elif symbol == ">":
                # Single right arrow
                points = [(center_x - 5, center_y), (center_x + 8, center_y - 10), (center_x + 8, center_y + 10)]
                pygame.draw.polygon(self.screen, self.TEXT_COLOR, points)
            elif symbol == ">>":
                # Double right arrows
                points1 = [(center_x - 5, center_y), (center_x + 5, center_y - 8), (center_x + 5, center_y + 8)]
                points2 = [(center_x + 10, center_y), (center_x + 20, center_y - 8), (center_x + 20, center_y + 8)]
                pygame.draw.polygon(self.screen, self.TEXT_COLOR, points1)
                pygame.draw.polygon(self.screen, self.TEXT_COLOR, points2)
            elif symbol == "||":
                # Pause bars
                pygame.draw.rect(self.screen, self.TEXT_COLOR, (center_x - 8, center_y - 10, 5, 20))
                pygame.draw.rect(self.screen, self.TEXT_COLOR, (center_x + 3, center_y - 10, 5, 20))
            
            x += button_width + spacing
        
        # Speed indicator (visual bar)
        speed_x = start_x
        speed_y = button_y + button_height + 15
        
        # Speed bar
        max_speed = 10.0
        speed_bar_width = 150
        speed_bar_height = 10
        speed_ratio = self.playback_speed / max_speed
        
        # Background
        pygame.draw.rect(self.screen, (80, 80, 80), 
                        (speed_x, speed_y, speed_bar_width, speed_bar_height))
        # Current speed
        pygame.draw.rect(self.screen, (0, 255, 0), 
                        (speed_x, speed_y, int(speed_bar_width * speed_ratio), speed_bar_height))
        # Border
        pygame.draw.rect(self.screen, self.TEXT_COLOR, 
                        (speed_x, speed_y, speed_bar_width, speed_bar_height), 1)
        
        # Draw small speed notches
        for i in range(6):
            notch_x = speed_x + int(speed_bar_width * i / 5)
            pygame.draw.line(self.screen, self.TEXT_COLOR,
                           (notch_x, speed_y + speed_bar_height),
                           (notch_x, speed_y + speed_bar_height + 5), 1)
    
    def prev_move(self):
        """Go to previous move."""
        self.playing = False
        self.current_move_idx = max(0, self.current_move_idx - 1)
    
    def next_move(self):
        """Go to next move."""
        game = self.get_current_game()
        if game:
            self.current_move_idx = min(game['total_moves'], self.current_move_idx + 1)
    
    def prev_game(self):
        """Go to previous game."""
        self.playing = False
        if self.games:
            self.current_game_idx = (self.current_game_idx - 1) % len(self.games)
            self.current_move_idx = 0
    
    def next_game(self):
        """Go to next game."""
        self.playing = False
        if self.games:
            self.current_game_idx = (self.current_game_idx + 1) % len(self.games)
            self.current_move_idx = 0
    
    def toggle_play(self):
        """Toggle autoplay."""
        self.playing = not self.playing
        self.last_update_time = pygame.time.get_ticks()
    
    def update_playback(self):
        """Update playback if playing."""
        if not self.playing:
            return
        
        current_time = pygame.time.get_ticks()
        time_per_move = 1000 / self.playback_speed  # milliseconds per move
        
        if current_time - self.last_update_time >= time_per_move:
            game = self.get_current_game()
            if game and self.current_move_idx < game['total_moves']:
                self.next_move()
                self.last_update_time = current_time
            else:
                self.playing = False
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.toggle_play()
                elif event.key == pygame.K_LEFT:
                    self.prev_move()
                elif event.key == pygame.K_RIGHT:
                    self.next_move()
                elif event.key == pygame.K_UP:
                    self.prev_game()
                elif event.key == pygame.K_DOWN:
                    self.next_game()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.playback_speed = min(10.0, self.playback_speed + 0.5)
                elif event.key == pygame.K_MINUS:
                    self.playback_speed = max(0.5, self.playback_speed - 0.5)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button_rect, callback, _ in self.buttons:
                    if button_rect.collidepoint(mouse_pos):
                        callback()
        
        return True
    
    def run(self):
        """Main visualization loop."""
        if not self.games:
            print("No games to visualize!")
            print(f"Please generate games first or check directory: {self.games_dir}")
            return
        
        running = True
        while running:
            running = self.handle_events()
            
            # Update
            self.update_playback()
            
            # Draw
            self.screen.fill(self.BACKGROUND)
            self.draw_board()
            self.draw_info_panel()
            self.draw_controls()
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()


def main():
    """Run the visualizer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize checkers training games")
    parser.add_argument("--games-dir", default="training_games",
                       help="Directory containing game pickle files")
    parser.add_argument("--square-size", type=int, default=70,
                       help="Size of each board square in pixels")
    
    args = parser.parse_args()
    
    visualizer = GameVisualizer(args.games_dir, args.square_size)
    visualizer.run()


if __name__ == "__main__":
    main()