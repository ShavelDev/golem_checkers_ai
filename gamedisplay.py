import pygame
import sys
import random
from checkers_types import Board, minimax_possiblemove

# ----------------------------------
# Your Board class goes here EXACTLY
# (UNCHANGED — paste everything above)
# ----------------------------------

# After pasting your class, continue here:

TILE = 80
BOARD_SIZE = TILE * 8
FPS = 60

pygame.init()
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
pygame.display.set_caption("Checkers – Using Given Board Type")
clock = pygame.time.Clock()

# Colors
LIGHT = (220, 220, 220)
DARK = (120, 80, 60)
RED = (200, 30, 30)      # opponent normal
GOLD = (255, 200, 0)     # opponent king
BLUE = (30, 80, 200)     # my normal
CYAN = (80, 200, 255)    # my king
HIGHLIGHT = (0, 255, 0)
CAPTURE_HIGHLIGHT = (255, 0, 0)  # Red highlight for captures

board_obj: Board = Board()
selected = None
legal_moves = []


def apply_move(move, y, x):
    """Apply a move to the board instance."""
    ny, nx = move['to']
    piece = board_obj.board[y][x]

    board_obj.board[y][x] = 0
    board_obj.board[ny][nx] = piece

    # capture
    if move["type"] == "capture":
        for cy, cx in  move["captures"]: 
        
            board_obj.board[cy][cx] = 0

    # promotion
    if move["promote"]:
        board_obj.board[ny][nx] = 2


def check_any_captures_available():
    """Check if any of the player's pieces can capture."""
    for y in range(8):
        for x in range(8):
            if board_obj.board[y][x] in (1, 2):  # Player's pieces
                moves = board_obj.get_possible_moves_for_piece(y, x)
                for move in moves:
                    if move['type'] == 'capture':
                        return True
    return False


# =============== Drawing ===============
def draw_board():
    for y in range(8):
        for x in range(8):
            color = DARK if (x + y) % 2 else LIGHT
            pygame.draw.rect(screen, color, (x*TILE, y*TILE, TILE, TILE))

            piece = board_obj.board[y][x]

            if piece != 0:
                if piece == 1:  color = BLUE
                elif piece == 2: color = CYAN
                elif piece == -1: color = RED
                elif piece == -2: color = GOLD

                pygame.draw.circle(
                    screen, color,
                    (x*TILE + TILE//2, y*TILE + TILE//2),
                    TILE//2 - 8
                )

    # highlight legal move destinations
    for mv in legal_moves:
        ny, nx = mv['to']
        # Use red highlight for captures, green for normal moves
        highlight_color = CAPTURE_HIGHLIGHT if mv['type'] == 'capture' else HIGHLIGHT
        pygame.draw.rect(screen, highlight_color,
                         (nx*TILE+20, ny*TILE+20, TILE-40, TILE-40), 3)


# =============== Utility ===============
def coords_from_mouse(pos):
    mx, my = pos
    return my // TILE, mx // TILE



def ai_opponent_minimax():
    board_obj.flipSides()

    best_board = minimax_possiblemove(board_obj, -10000, 10000, depth=6, returnBoard=True)

    if best_board is None:
        print("AI has no moves!")
        board_obj.flipSides()
        return False
    
    print(f"best_board type: {type(best_board)}")
    board_obj.board = best_board

    board_obj.flipSides()
    return True


# =============== AI ===============
def ai_random_move():
    """Opponent (-1, -2) makes a random legal move."""

    # temporarily flip sides so AI sees pieces as (1,2)
    board_obj.flipSides()
    _, moves = board_obj.returnPossibleMoves()
    # moves is list of boards, but we need individual piece moves

    if moves:
        board_obj.board = random.choice(moves)

    board_obj.flipSides()



# =============== Main Loop ===============
running = True
player_turn = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if player_turn and event.type == pygame.MOUSEBUTTONDOWN:
            y, x = coords_from_mouse(event.pos)
            piece = board_obj.board[y][x]

            # Check if any captures are available
            any_captures = check_any_captures_available()

            # Select piece
            if piece in (1,2):
                selected = (y, x)
                legal_moves = board_obj.get_possible_moves_for_piece(y, x)
                
                # FORCED CAPTURE RULE: If any piece can capture, only show capture moves
                if any_captures:
                    legal_moves = [mv for mv in legal_moves if mv['type'] == 'capture']
                    # If this piece has no captures, don't select it
                    if not legal_moves:
                        selected = None
                        legal_moves = []

            # Make move
            elif selected:
                sy, sx = selected
                for mv in legal_moves:
                    if mv["to"] == (y, x):
                        apply_move(mv, sy, sx)
                        selected = None
                        legal_moves = []
                        player_turn = False  # switch turn
                        break

    # AI MOVE
    if not player_turn:
        pygame.time.delay(300)
        
        success = ai_opponent_minimax()
        
        if not success:
            print("Player wins! AI has no moves.")
        
        player_turn = True

    draw_board()
    pygame.display.flip()