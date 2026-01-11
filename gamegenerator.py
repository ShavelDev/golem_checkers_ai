import pickle
import os
from datetime import datetime
from checkers_types import Board, minimax_possiblemove
import random


class GameGenerator:
    """
    Generate checkers games between two minimax bots with different depths.
    Each game is saved as a pickle file containing training data.
    """
    
    def __init__(self, output_dir="training_games"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_game(self, player1_depth=5, player2_depth=2, max_moves=200, random_move_chance=0.0, initial_random_moves=0):
        """
        Generate a single game between two bots.
        
        Args:
            player1_depth: Minimax depth for the stronger bot
            player2_depth: Minimax depth for the weaker bot
            max_moves: Maximum number of moves before declaring draw
            random_move_chance: Probability (0.0-1.0) of making a random move instead of minimax
            
        Returns:
            Dictionary containing game data
        """
        board = Board()
        game_history = []
        move_count = 0
        current_player = 1  # 1 = strong bot, -1 = weak bot
        
        print(f"\n{'='*60}")
        print(f"Starting new game: Strong(depth={player1_depth}) vs Weak(depth={player2_depth})")
        print(f"{'='*60}")
        
        while move_count < max_moves:
            move_count += 1
            
            # Determine which bot is playing
            if current_player == 1:
                depth = player1_depth
                player_name = "Strong"
            else:
                depth = player2_depth
                player_name = "Weak"
            
            # Store the board BEFORE any flipping (from strong bot's perspective always)
            board_before_standard = [row[:] for row in board.board]
            
            # Get current board state (from perspective of current player)
            if current_player == -1:
                board.flipSides()
            
            # Check if current player has any moves
            _, possible_moves = board.returnPossibleMoves()
            
            if not possible_moves:
                # Current player has no moves - they lose
                winner = -current_player
                print(f"\nMove {move_count}: {player_name} has no moves - loses!")
                
                # Flip back if we flipped
                if current_player == -1:
                    board.flipSides()
                break
            
            # Decide whether to use minimax or random move
            use_random = initial_random_moves > 0 or random.random() < random_move_chance
            if initial_random_moves > 0:
                initial_random_moves -= 1
            
            if use_random:
                # Make a random move from available options
                best_board = random.choice(possible_moves)
                move_type = "random"
            else:
                # Get best move using minimax
                best_board = minimax_possiblemove(
                    board,
                    alpha=-10000,
                    beta=10000,
                    isMaximizing=True,
                    depth=depth,
                    returnBoard=True
                )
                move_type = "minimax"
            
            if best_board is None:
                # No valid move found - current player loses
                winner = -current_player
                print(f"\nMove {move_count}: {player_name} cannot find valid move - loses!")
                
                if current_player == -1:
                    board.flipSides()
                break
            
            # Apply the move
            board.board = best_board
            
            # Flip back to standard perspective (strong bot's view)
            if current_player == -1:
                board.flipSides()
            
            # Store the board AFTER move (from strong bot's perspective)
            board_after_standard = [row[:] for row in board.board]
            
            # Create squeezed versions
            squeezed_before = Board(board_before_standard).squeeze()
            squeezed_after = Board(board_after_standard).squeeze()
            
            # Calculate board value from strong bot's perspective (always from current standard board)
            board_value = board.estimateAdvantage()
            
            # Store move in history
            move_data = {
                'move_number': move_count,
                'player': current_player,
                'board_before_8x8': board_before_standard,
                'board_after_8x8': board_after_standard,
                'board_before_4x8': squeezed_before,
                'board_after_4x8': squeezed_after,
                'board_value': board_value,
                'depth_used': depth,
                'move_type': move_type  # 'minimax' or 'random'
            }
            game_history.append(move_data)
            
            # Print progress every 10 moves
            if move_count % 10 == 0:
                print(f"Move {move_count}: {player_name} played (value={board_value:.2f})")
            
            # Check for draw by insufficient material
            piece_count = sum(1 for row in board.board for cell in row if cell != 0)
            if piece_count <= 2:
                winner = 0  # Draw
                print(f"\nMove {move_count}: Draw by insufficient material")
                break
            
            # Switch players
            current_player *= -1
        
        else:
            # Max moves reached - declare draw
            winner = 0
            print(f"\nMove {move_count}: Draw by move limit")
        
        # Create game summary
        game_data = {
            'game_id': datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            'player1_depth': player1_depth,
            'player2_depth': player2_depth,
            'random_move_chance': random_move_chance,
            'total_moves': move_count,
            'winner': winner,  # 1 = strong bot, -1 = weak bot, 0 = draw
            'winner_name': 'Strong' if winner == 1 else ('Weak' if winner == -1 else 'Draw'),
            'move_history': game_history,
            'final_board': board.board,
            'final_board_squeezed': board.squeeze()
        }
        
        return game_data
    
    def save_game(self, game_data):
        """Save game data to a pickle file."""
        filename = f"game_{game_data['game_id']}.pkl"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'wb') as f:
            pickle.dump(game_data, f)
        
        print(f"\nGame saved to: {filepath}")
        print(f"Winner: {game_data['winner_name']}")
        print(f"Total moves: {game_data['total_moves']}")
        return filepath
    
    def generate_games(self, num_games, player1_depth=5, player2_depth=2, max_moves=200, random_move_chance=0.0, initial_random_moves=5):
        """
        Generate multiple games and save them.
        
        Args:
            num_games: Number of games to generate
            player1_depth: Minimax depth for stronger bot
            player2_depth: Minimax depth for weaker bot
            max_moves: Maximum moves per game
            random_move_chance: Probability (0.0-1.0) of making random moves instead of minimax
            
        Returns:
            List of filepaths to saved games
        """
        saved_games = []
        
        print(f"\n{'#'*60}")
        print(f"# Generating {num_games} games")
        print(f"# Strong bot depth: {player1_depth}")
        print(f"# Weak bot depth: {player2_depth}")
        print(f"# Random move chance: {random_move_chance*100:.1f}%")
        print(f"# Max moves per game: {max_moves}")
        print(f"{'#'*60}")
        
        for i in range(num_games):
            print(f"\n\n{'*'*60}")
            print(f"* GAME {i+1}/{num_games}")
            print(f"{'*'*60}")
            
            try:
                game_data = self.generate_game(player1_depth, player2_depth, max_moves, random_move_chance, initial_random_moves)
                filepath = self.save_game(game_data)
                saved_games.append(filepath)
            except Exception as e:
                print(f"\nError generating game {i+1}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n\n{'#'*60}")
        print(f"# Generation complete!")
        print(f"# Successfully generated: {len(saved_games)}/{num_games} games")
        print(f"# Games saved to: {self.output_dir}")
        print(f"{'#'*60}\n")
        
        return saved_games
    
    def load_game(self, filepath):
        """Load a game from a pickle file."""
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    def print_game_summary(self, filepath):
        """Print a summary of a saved game."""
        game_data = self.load_game(filepath)
        
        print(f"\n{'='*60}")
        print(f"Game ID: {game_data['game_id']}")
        print(f"Strong depth: {game_data['player1_depth']}")
        print(f"Weak depth: {game_data['player2_depth']}")
        print(f"Total moves: {game_data['total_moves']}")
        print(f"Winner: {game_data['winner_name']}")
        print(f"{'='*60}")
        
        # Show first few moves
        print("\nFirst 5 moves:")
        for move in game_data['move_history'][:5]:
            player_name = "Strong" if move['player'] == 1 else "Weak"
            print(f"  Move {move['move_number']}: {player_name} "
                  f"(depth={move['depth_used']}, value={move['board_value']:.2f})")
        
        if len(game_data['move_history']) > 5:
            print("  ...")


def main():
    """Example usage of the game generator."""
    generator = GameGenerator(output_dir="training_games")
    
    # Generate 5 games with different depth combinations
    print("Generating games with varied bot strengths...")
    
    # Games with depth 5 vs depth 2, pure minimax
    #generator.generate_games(num_games=2, player1_depth=5, player2_depth=2, max_moves=50, random_move_chance=0.5, initial_random_moves=10)
    generator.generate_games(num_games=1000, player1_depth=5, player2_depth=1, max_moves=60, random_move_chance=0.5, initial_random_moves=5)
    generator.generate_games(num_games=1000, player1_depth=1, player2_depth=5, max_moves=60, random_move_chance=0.5, initial_random_moves=5)
    
    generator.generate_games(num_games=1000, player1_depth=2, player2_depth=3, max_moves=60, random_move_chance=0.3, initial_random_moves=5)
    generator.generate_games(num_games=1000, player1_depth=3, player2_depth=2, max_moves=60, random_move_chance=0.3, initial_random_moves=5)
    
    generator.generate_games(num_games=1000, player1_depth=1, player2_depth=2, max_moves=60, random_move_chance=0.1, initial_random_moves=5)
    generator.generate_games(num_games=1000, player1_depth=2, player2_depth=1, max_moves=60, random_move_chance=0.1, initial_random_moves=5)
    
    generator.generate_games(num_games=1000, player1_depth=4, player2_depth=2, max_moves=60, random_move_chance=0.3, initial_random_moves=5)
    generator.generate_games(num_games=1000, player1_depth=2, player2_depth=4, max_moves=60, random_move_chance=0.3, initial_random_moves=5)
    
    generator.generate_games(num_games=1000, player1_depth=3, player2_depth=1, max_moves=60, random_move_chance=0.3, initial_random_moves=5)
    generator.generate_games(num_games=1000, player1_depth=1, player2_depth=3, max_moves=60, random_move_chance=0.3, initial_random_moves=5)
    
    generator.generate_games(num_games=1000, player1_depth=3, player2_depth=2, max_moves=60, random_move_chance=0.3, initial_random_moves=5)
    generator.generate_games(num_games=1000, player1_depth=2, player2_depth=3, max_moves=60, random_move_chance=0.3, initial_random_moves=5)
    
    

    # Show summary of first generated game
    game_files = [f for f in os.listdir("training_games") if f.endswith('.pkl')]
    if game_files:
        print("\n\nExample game summary:")
        generator.print_game_summary(os.path.join("training_games", game_files[0]))


if __name__ == "__main__":
    main()