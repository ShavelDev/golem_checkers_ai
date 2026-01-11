# from functools import cached_property,

# general rules:
# -2 - opponent king
# -1 - opponent piece
#  1 - my piece
#  2 - my king
#  0 - empty

class Board():
    
    def __init__(self, board=None):
        if board is None:
            board = [
                [ 0, -1,  0, -1,  0, -1,  0, -1],
                [-1,  0, -1,  0, -1,  0, -1,  0],
                [ 0, -1,  0, -1,  0, -1,  0, -1],
                [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 1,  0,  1,  0,  1,  0,  1,  0],
                [ 0,  1,  0,  1,  0,  1,  0,  1],
                [ 1,  0,  1,  0,  1,  0,  1,  0]
            ]
        elif isinstance(board, Board):
            assert(False)
        self.board = board
    

    def squeeze(self):
        """Return a 4×8 board containing only playable (dark) squares."""
        squeezed = []
        for r in range(8):
            if r % 2 == 0:       # even rows → take columns 1,3,5,7
                squeezed.append([self.board[r][c] for c in (1, 3, 5, 7)])
            else:               # odd rows → take columns 0,2,4,6
                squeezed.append([self.board[r][c] for c in (0, 2, 4, 6)])
        return squeezed  # list of 8 rows of 4 elements

    def flipSides(self):
        """Multiply each board cell by -1 (swap sides)."""

        for r in range(8):
            for c in range(8):
                self.board[r][c] *= -1


        self.board = [row[::-1] for row in self.board[::-1]]
        return self  
    
    def display_board(self):
        """
        print the board stored in a Board() instance.
        """
        
        symbols = {
            -2: "OK",   # opponent king
            -1: "O",    # opponent piece
            0: "+",    # empty
            1: "X",    # my piece
            2: "MK"    # my king
        }

        print("   0  1  2  3  4  5  6  7")
        print("  ------------------------")
        for r in range(8):
            row_str = f"{r}| "
            for c in range(8):
                row_str += f"{symbols[self.board[r][c]]:2} "
            print(row_str)

    def estimateAdvantage(self):
        """
        Estimate the advantage according to the board provided.
        Enhanced evaluation with positional bonuses.
        """
        score = 0.0
        
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                piece = self.board[y][x]
                
                if piece == 0:
                    continue
                    
                # Material value
                if abs(piece) == 1:
                    piece_value = 3.0
                else:  # King
                    piece_value = 5.0
                
                # Positional bonuses
                positional_bonus = 0.0
                
                # Reward advancement for regular pieces
                if piece == 1:  # My regular piece
                    positional_bonus += (7 - y) * 0.1  # Closer to promotion
                elif piece == -1:  # Opponent regular piece
                    positional_bonus += y * 0.1  # Their advancement
                
                # Center control bonus
                center_distance = abs(3.5 - x) + abs(3.5 - y)
                positional_bonus += (7 - center_distance) * 0.05
                
                # Back row protection bonus for pieces
                if piece == 1 and y == 7:
                    positional_bonus += 0.3
                elif piece == -1 and y == 0:
                    positional_bonus += 0.3
                
                # Apply value with sign
                if piece > 0:
                    score += piece_value + positional_bonus
                else:
                    score -= piece_value + positional_bonus
        
        return score
    

    def get_possible_moves_for_piece(self, y, x):
        """
        Return all possible moves for the piece at (y, x).
        Supports multi-capture with proper "must capture" rule.
        """

        rows = len(self.board)
        cols = len(self.board[0])

        def inside(r, c):
            return 0 <= r < rows and 0 <= c < cols

        piece = self.board[y][x]
        if piece == 0:
            return []

        is_king = abs(piece) == 2
        is_current_player = piece > 0

        if is_current_player:
            forward_dirs = [(-1, -1), (-1, 1)]
            promotion_row = 0
            enemy_pieces = (-1, -2)
        else:
            forward_dirs = [(1, -1), (1, 1)]
            promotion_row = rows - 1
            enemy_pieces = (1, 2)

        directions = forward_dirs
        if is_king:
            directions = forward_dirs + [(-d[0], d[1]) for d in forward_dirs]

        # -----------------------------
        # MULTI-CAPTURE SEARCH
        # -----------------------------
        capture_sequences = []

        def dfs(board, cy, cx, path, captured):
            """DFS to find all possible capture sequences from current position."""
            found_further = False

            for dy, dx in directions:
                by, bx = cy + dy, cx + dx
                jy, jx = cy + 2 * dy, cx + 2 * dx

                if inside(by, bx) and inside(jy, jx):
                    # Check if we can capture (and haven't captured this piece already)
                    if board[by][bx] in enemy_pieces and board[jy][jx] == 0 and (by, bx) not in captured:
                        found_further = True

                        # Create new board state after this capture
                        new_board = [row[:] for row in board]
                        new_board[jy][jx] = new_board[cy][cx]
                        new_board[cy][cx] = 0
                        new_board[by][bx] = 0

                        # Continue searching for more captures
                        dfs(
                            new_board,
                            jy,
                            jx,
                            path + [(jy, jx)],
                            captured + [(by, bx)]
                        )

            # If no further captures found and we've captured at least one piece
            if not found_further and captured:
                promote = (not is_king and cy == promotion_row)
                capture_sequences.append({
                    'to': (cy, cx),
                    'type': 'capture',
                    'path': path,
                    'captures': captured,
                    'promote': promote
                })

        dfs(self.board, y, x, [(y, x)], [])

        # If any capture exists → must take captures (forced capture rule)
        if capture_sequences:
            return capture_sequences

        # -----------------------------
        # NORMAL MOVES (only if no capture possible)
        # -----------------------------
        moves = []
        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            if inside(ny, nx) and self.board[ny][nx] == 0:
                promote = (not is_king and ny == promotion_row)
                moves.append({
                    'to': (ny, nx),
                    'type': 'move',
                    'captures': [],
                    'promote': promote
                })

        return moves


    def returnPossibleMoves(self, forOpponent=False):
        """
        Return all possible boards after legal moves.
        Implements the "must capture" rule: if any capture is available,
        only capture moves are returned.
        
        forOpponent=False → current player (1, 2)
        forOpponent=True  → opponent (-1, -2)
        
        Returns: (capture_detected, list_of_boards)
        """

        result_boards = []
        board = self.board

        def clone_board(b):
            return [row[:] for row in b]

        rows = len(board)
        cols = len(board[0]) if rows else 0

        valid_pieces = (-1, -2) if forOpponent else (1, 2)
        capture_boards = []
        normal_boards = []

        for y in range(rows):
            for x in range(cols):
                if board[y][x] not in valid_pieces:
                    continue

                moves = self.get_possible_moves_for_piece(y, x)

                for move in moves:
                    ny, nx = move['to']
                    new_board = clone_board(board)

                    # Move piece to destination
                    new_board[ny][nx] = new_board[y][x]
                    new_board[y][x] = 0

                    # Remove all captured pieces
                    if move['type'] == 'capture':
                        for by, bx in move['captures']:
                            new_board[by][bx] = 0

                    # Handle promotion
                    if move['promote']:
                        new_board[ny][nx] = 2 if new_board[ny][nx] > 0 else -2

                    # Separate captures from normal moves
                    if move['type'] == 'capture':
                        capture_boards.append(new_board)
                    else:
                        normal_boards.append(new_board)

        # Must capture rule: if any captures exist, only return captures
        if capture_boards:
            return (True, capture_boards)
        else:
            return (False, normal_boards)


def minimax_possiblemove(
    board: Board,
    alpha: int,
    beta: int,
    isMaximizing: bool = True,
    depth: int = 5,
    returnBoard: bool = False
):
    """
    Minimax with alpha-beta pruning.
    
    CRITICAL FIX: Multi-captures are already handled by get_possible_moves_for_piece()
    which returns complete multi-capture sequences. Each board in returnPossibleMoves
    represents a COMPLETE turn (including all forced multi-captures).
    
    Therefore, we ALWAYS switch players after applying a move from returnPossibleMoves.
    """
    assert(not (isMaximizing == False and returnBoard == True))
    
    if depth == 0:
        score = board.estimateAdvantage()
        if not isMaximizing:
            score *= -1
        return score
    
    if isMaximizing:
        maxeval = -10000
        best_board = None

        _, childboards = board.returnPossibleMoves()
        
        # If no moves available, this is a loss
        if not childboards:
            return -10000
        
        for childb in childboards:
            child_obj = Board(childb)
            
            # ALWAYS switch to opponent after a complete move
            # (multi-captures are already complete in the board state)
            eval = minimax_possiblemove(
                child_obj, alpha, beta, 
                isMaximizing=False,  # Always switch to minimizing
                depth=depth-1
            )
            
            if eval > maxeval:
                maxeval = eval
                best_board = childb

            alpha = max(alpha, eval)
            if beta <= alpha:
                break

        return best_board if returnBoard else maxeval
    
    else:  # Minimizing (opponent's turn)
        mineval = 10000
        
        _, childboards = board.returnPossibleMoves(forOpponent=True)
        
        # If no moves available, this is a win for us
        if not childboards:
            return 10000
        
        for childb in childboards:
            child_obj = Board(childb)
            
            # ALWAYS switch to maximizing player after opponent's complete move
            eval = minimax_possiblemove(
                child_obj, alpha, beta, 
                isMaximizing=True,  # Always switch to maximizing
                depth=depth-1
            )
            
            mineval = min(mineval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
                
        return mineval


def minimax_debug(
    board: Board,
    alpha: int,
    beta: int,
    isMaximizing: bool = True,
    depth: int = 5,
    indent: int = 0,
    returnBoard: bool = False
):
    """Debug version of minimax that prints the search tree."""
    prefix = "│   " * indent
    player = "MAX" if isMaximizing else "MIN"

    print(f"{prefix}▶ {player} | depth={depth} | α={alpha} β={beta}")
    
    if depth == 0:
        score = board.estimateAdvantage()
        if not isMaximizing:
            score *= -1
        print(f"{prefix}✔ Leaf score = {score}")
        return score

    if isMaximizing:
        maxeval = -10000
        best_board = None

        _, childboards = board.returnPossibleMoves()

        if not childboards:
            print(f"{prefix}✘ No moves - LOSS")
            return -10000

        print(f"{prefix}Found {len(childboards)} moves")

        for i, childb in enumerate(childboards):
            print(f"{prefix}─ Move {i+1}/{len(childboards)}")
            child_obj = Board(childb)

            eval = minimax_debug(
                child_obj,
                alpha,
                beta,
                isMaximizing=False,
                depth=depth - 1,
                indent=indent + 1
            )

            print(f"{prefix}  Eval = {eval}")

            if eval > maxeval:
                maxeval = eval
                best_board = childb

            alpha = max(alpha, eval)
            print(f"{prefix}  Updated α={alpha}")

            if beta <= alpha:
                print(f"{prefix}✂ PRUNE (β ≤ α)")
                break

        print(f"{prefix}◀ MAX returns {maxeval}")
        return best_board if returnBoard else maxeval

    else:
        mineval = 10000

        _, childboards = board.returnPossibleMoves(forOpponent=True)

        if not childboards:
            print(f"{prefix}✘ No moves - WIN")
            return 10000

        print(f"{prefix}Found {len(childboards)} opponent moves")

        for i, childb in enumerate(childboards):
            print(f"{prefix}─ Opponent move {i+1}/{len(childboards)}")
            child_obj = Board(childb)

            eval = minimax_debug(
                child_obj,
                alpha,
                beta,
                isMaximizing=True,
                depth=depth - 1,
                indent=indent + 1
            )

            mineval = min(mineval, eval)
            beta = min(beta, eval)

            print(f"{prefix}  Updated β={beta}")

            if beta <= alpha:
                print(f"{prefix}✂ PRUNE (β ≤ α)")
                break

        print(f"{prefix}◀ MIN returns {mineval}")
        return mineval