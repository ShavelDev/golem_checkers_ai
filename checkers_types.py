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
        return self  # allow chaining
    
    def display_board(self):
        """
        Pretty-print the board stored in a Board() instance.
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
        Estimate the advantage accordint to the board provided
        """
        score : int = 0
        for y in len(self.board):
            for x in len(self.board[y]):
                score += self.board[y][x]


    def get_possible_moves_for_piece(self,  y, x):
        """
        Return a list of possible moves for the piece at (y, x) on `board`.
        Each move is a dict:
            {
                'to': (ny, nx),
                'type': 'move' or 'capture',
                'capture': (by, bx) or None,
                'promote': True/False
            }
        Works for normal pieces (1) which move "up" (y-1) and kings (2) which move in all four diagonals.
        Assumes current player's pieces are 1 (man) and 2 (king); opponents are -1 (man) and -2 (king).
        """
        rows = len(self.board)
        cols = len(self.board[0]) if rows else 0

        def inside(yy, xx):
            return 0 <= yy < rows and 0 <= xx < cols

        piece = self.board[y][x]
        if piece not in (1, 2):
            return []  # nothing to do for empty or opponent pieces

        # Directions: normal pieces move upward (toward y-1), kings in all 4 diagonals
        directions_normal = [(-1, -1), (-1, 1)]
        directions_king   = directions_normal + [(1, -1), (1, 1)]
        dirs = directions_king if piece == 2 else directions_normal

        moves = []
        for dy, dx in dirs:
            ny, nx = y + dy, x + dx

            # --- normal (non-capturing) move ---
            if inside(ny, nx) and self.board[ny][nx] == 0:
                promote = (piece == 1 and ny == 0)  # promote if a normal piece reaches top row
                moves.append({
                    'to': (ny, nx),
                    'type': 'move',
                    'capture': None,
                    'promote': promote
                })

            # --- capture (jump) ---
            by, bx = ny, nx                    # intermediate square (must contain opponent)
            jy, jx = y + 2*dy, x + 2*dx       # landing square after the jump

            if inside(by, bx) and inside(jy, jx):
                if self.board[by][bx] in (-1, -2) and self.board[jy][jx] == 0:
                    promote = (piece == 1 and jy == 0)
                    moves.append({
                        'to': (jy, jx),
                        'type': 'capture',
                        'capture': (by, bx),
                        'promote': promote
                    })

        return moves


    def returnPossibleMoves(self):
        """
        Return a list of boards (deep copies) after every legal move for the
        current player (pieces 1 and 2). Captures are included (single-captures).
        The helper get_possible_moves_for_piece returns capture info and returnPossibleMoves
        applies captures (removes the jumped piece) when creating the new board.
        """
        result_boards = []
        board = self.board

        # Helper: clone board deeply
        def clone_board(b):
            return [row[:] for row in b]

        rows = len(board)
        cols = len(board[0]) if rows else 0

        for y in range(rows):
            for x in range(cols):
                piece = board[y][x]

                if piece not in (1, 2):
                    continue

                possible_moves = self.get_possible_moves_for_piece( y, x)

                for move in possible_moves:
                    ny, nx = move['to']
                    new_board = clone_board(board)

                    # Move piece
                    new_board[ny][nx] = new_board[y][x]
                    new_board[y][x] = 0

                    # If it's a capture, remove the opponent
                    if move['type'] == 'capture' and move['capture'] is not None:
                        by, bx = move['capture']
                        new_board[by][bx] = 0

                    # Handle promotion
                    if move['promote']:
                        new_board[ny][nx] = 2

                    result_boards.append(new_board)

        return result_boards
