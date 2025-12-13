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

    # @property
    def estimateAdvantage(self):
        """
        Estimate the advantage accordint to the board provided
        """
        score : int = 0
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                score += self.board[y][x]

        return score
    
    def get_possible_moves_for_piece(self, y, x):
        """
        Return a list of possible moves for the piece at (y, x).
        Works for:
        - Current player:  1 (man),  2 (king)
        - Opponent:       -1 (man), -2 (king)
        """

        rows = len(self.board)
        cols = len(self.board[0]) if rows else 0

        def inside(yy, xx):
            return 0 <= yy < rows and 0 <= xx < cols

        piece = self.board[y][x]
        if piece == 0:
            return []

        moves = []

        is_king = abs(piece) == 2
        is_current_player = piece > 0

        # Direction of normal men
        if is_current_player:
            forward_dirs = [(-1, -1), (-1, 1)]   # move up
            promotion_row = 0
            enemy_pieces = (-1, -2)
        else:
            forward_dirs = [(1, -1), (1, 1)]     # move down
            promotion_row = rows - 1
            enemy_pieces = (1, 2)

        directions = forward_dirs
        if is_king:
            directions = forward_dirs + [(-d[0], d[1]) for d in forward_dirs]

        for dy, dx in directions:
            ny, nx = y + dy, x + dx

            # --- normal move ---
            if inside(ny, nx) and self.board[ny][nx] == 0:
                promote = (not is_king and ny == promotion_row)
                moves.append({
                    'to': (ny, nx),
                    'type': 'move',
                    'capture': None,
                    'promote': promote
                })

            # --- capture ---
            by, bx = ny, nx
            jy, jx = y + 2 * dy, x + 2 * dx

            if inside(by, bx) and inside(jy, jx):
                if self.board[by][bx] in enemy_pieces and self.board[jy][jx] == 0:
                    promote = (not is_king and jy == promotion_row)
                    moves.append({
                        'to': (jy, jx),
                        'type': 'capture',
                        'capture': (by, bx),
                        'promote': promote
                    })

        return moves


    # def get_possible_moves_for_piece(self,  y, x):
    #     """
    #     Return a list of possible moves for the piece at (y, x) on `board`.
    #     Each move is a dict:
    #         {
    #             'to': (ny, nx),
    #             'type': 'move' or 'capture',
    #             'capture': (by, bx) or None,
    #             'promote': True/False
    #         }
    #     Works for normal pieces (1) which move "up" (y-1) and kings (2) which move in all four diagonals.
    #     Assumes current player's pieces are 1 (man) and 2 (king); opponents are -1 (man) and -2 (king).
    #     """
    #     rows = len(self.board)
    #     cols = len(self.board[0]) if rows else 0

    #     def inside(yy, xx):
    #         return 0 <= yy < rows and 0 <= xx < cols

    #     piece = self.board[y][x]
    #     if piece not in (1, 2):
    #         return []  # nothing to do for empty or opponent pieces

    #     # Directions: normal pieces move upward (toward y-1), kings in all 4 diagonals
    #     directions_normal = [(-1, -1), (-1, 1)]
    #     directions_king   = directions_normal + [(1, -1), (1, 1)]
    #     dirs = directions_king if piece == 2 else directions_normal

    #     moves = []
    #     for dy, dx in dirs:
    #         ny, nx = y + dy, x + dx

    #         # --- normal (non-capturing) move ---
    #         if inside(ny, nx) and self.board[ny][nx] == 0:
    #             promote = (piece == 1 and ny == 0)  # promote if a normal piece reaches top row
    #             moves.append({
    #                 'to': (ny, nx),
    #                 'type': 'move',
    #                 'capture': None,
    #                 'promote': promote
    #             })

    #         # --- capture (jump) ---
    #         by, bx = ny, nx                    # intermediate square (must contain opponent)
    #         jy, jx = y + 2*dy, x + 2*dx       # landing square after the jump

    #         if inside(by, bx) and inside(jy, jx):
    #             if self.board[by][bx] in (-1, -2) and self.board[jy][jx] == 0:
    #                 promote = (piece == 1 and jy == 0)
    #                 moves.append({
    #                     'to': (jy, jx),
    #                     'type': 'capture',
    #                     'capture': (by, bx),
    #                     'promote': promote
    #                 })

    #     return moves
    



    # def returnPossibleMoves(self, forOpponent = False):
    #     """
    #     Return a list of boards (deep copies) after every legal move for the
    #     current player (pieces 1 and 2). Captures are included (single-captures).
    #     The helper get_possible_moves_for_piece returns capture info and returnPossibleMoves
    #     applies captures (removes the jumped piece) when creating the new board.
    #     """

        
    #     result_boards = []
    #     board = self.board

    #     # Helper: clone board deeply
    #     def clone_board(b):
    #         return [row[:] for row in b]

    #     rows = len(board)
    #     cols = len(board[0]) if rows else 0

    #     for y in range(rows):
    #         for x in range(cols):
    #             piece = board[y][x]

    #             if piece not in (1, 2):
    #                 continue

    #             possible_moves = self.get_possible_moves_for_piece( y, x)

    #             for move in possible_moves:
    #                 ny, nx = move['to']
    #                 new_board = clone_board(board)

    #                 # Move piece
    #                 new_board[ny][nx] = new_board[y][x]
    #                 new_board[y][x] = 0

    #                 # If it's a capture, remove the opponent
    #                 if move['type'] == 'capture' and move['capture'] is not None:
    #                     by, bx = move['capture']
    #                     new_board[by][bx] = 0

    #                 # Handle promotion
    #                 if move['promote']:
    #                     new_board[ny][nx] = 2

    #                 result_boards.append(new_board)

    #     return result_boards

    def returnPossibleMoves(self, forOpponent=False):
        """
        Return all possible boards after legal moves.
        forOpponent=False → current player (1, 2)
        forOpponent=True  → opponent (-1, -2)
        """

        result_boards = []
        board = self.board

        def clone_board(b):
            return [row[:] for row in b]

        rows = len(board)
        cols = len(board[0]) if rows else 0

        valid_pieces = (-1, -2) if forOpponent else (1, 2)

        for y in range(rows):
            for x in range(cols):
                if board[y][x] not in valid_pieces:
                    continue

                moves = self.get_possible_moves_for_piece(y, x)

                for move in moves:
                    ny, nx = move['to']
                    new_board = clone_board(board)

                    new_board[ny][nx] = new_board[y][x]
                    new_board[y][x] = 0

                    if move['type'] == 'capture':
                        by, bx = move['capture']
                        new_board[by][bx] = 0

                    if move['promote']:
                        new_board[ny][nx] = 2 if new_board[ny][nx] > 0 else -2

                    result_boards.append(new_board)

        return result_boards
    

def minimax_possiblemove( board: Board ,  alpha: int, beta: int, isMaximizing = True, depth: int = 5, returnBoard = False):
    assert( not (isMaximizing == False and returnBoard == True))
    
    if depth == 0:
        # print(type(board))
        score = board.estimateAdvantage()
        if not isMaximizing:
            score *= -1
        return score
    
    
    if isMaximizing :
        maxeval = -1000
        best_board = None

        childboards = board.returnPossibleMoves()
        for childb in childboards:
            
            eval = minimax_possiblemove(Board(childb), alpha, beta, isMaximizing=False, depth=depth-1)
            if returnBoard:
                print(eval)
            # maxeval = max(maxeval, eval)
            if eval > maxeval:
                maxeval = eval
                best_board = childb

            alpha = max(alpha, eval)
            if beta <= alpha:
                break

        if returnBoard:
            print(f"maxeval: {maxeval}")
        return best_board if returnBoard else maxeval
    
    else:
        mineval = 1000
        # board.flipSides()
        childboards  = board.returnPossibleMoves(forOpponent=True)
        for childb in childboards:
            childb = Board(childb)
            # childb.flipSides()

            eval = minimax_possiblemove(childb, alpha, beta, isMaximizing=True, depth=depth-1)
            mineval = min(mineval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return mineval

  

    # def minimax_possiblemove(self, depth: int = 5, curr_depth: int = 0, board:Board = None):

    #     if board == None:
    #         boards: list[Board] = self.returnPossibleMoves()
    #         #sort them according to score
    #         boards = sorted(boards, key=lambda obj: obj.estimateAdvantage, reverse=True)
    #         highestEstimation = boards[0].estimateAdvantage

    #         for b in boards:

    #             if b.estimateAdvantage != highestEstimation:
    #                 break

    #             b.minimax_possiblemove(
    #                 depth=depth, 
    #                 curr_depth = curr_depth + 1,
    #                 board = b
    #             )

                


    #     elif curr_depth != depth:
    #         boards: list[Board] = board.returnPossibleMoves()
    #         boards = sorted(boards, key=lambda obj: obj.estimateAdvantage, reverse=True)
    #         highestEstimation = boards[0].estimateAdvantage

    #         for b in boards:

    #             if b.estimateAdvantage != highestEstimation:
    #                 break

    #             b.minimax_possiblemove(
    #                 depth=depth, 
    #                 curr_depth = curr_depth + 1,
    #                 board = b
    #             )





             


        
