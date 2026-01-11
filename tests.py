from checkers_types import Board, minimax_debug, minimax_possiblemove


#test 1
print("\n\ntest1\n")


board = Board()

print(board.squeeze())
print("\n")
board.display_board()


#test 2
print("\n\ntest2\n")


board = Board()

print("boards\n")
_, boards = board.returnPossibleMoves()
for b in boards:
    print(f"shape b: y:{len(b)} x:{(len(b[0]))}")
    
    print(Board(b).display_board())


#test 3
print("\n\ntest3\n")


board = Board([
                [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  2],
                [ 0,  0,  0,  0,  0,  0,  -1,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0]
            ])

print(board.display_board())

print("possible moves\n")
_, boards = board.returnPossibleMoves()
for  b in boards:
    print(f"shape b: y:{len(b)} x:{(len(b[0]))}")
    
    print(Board(b).display_board())


#test 5
print("\n\ntest5\n")
board = Board([
                [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  -1,  0,  -1],
                [ 0,  0,  0,  0,  0,  0,  1,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0]
            ])

print(board.display_board())

print(board.get_possible_moves_for_piece(x=6, y=4))


#test 6
print("\n\ntest6\n")
board = Board([
                [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  1,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  -1,  0,  -1],
                [ 0,  0,  0,  0,  0,  0,  1,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0]
            ])

print(board.display_board())

print(board.get_possible_moves_for_piece(x=2, y=1))

print("possible moves\n")
_, boards = board.returnPossibleMoves()
for b in boards:
    print(f"shape b: y:{len(b)} x:{(len(b[0]))}")
    
    print(Board(b).display_board())



#test 7
print("\n\ntest7\n")
board = Board([
                [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  -1,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  -1,  0,  -1],
                [ 0,  0,  0,  0,  0,  0,  1,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  -1,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0]
            ])

print(board.display_board())

# print(board.get_possible_moves_for_piece(x=2, y=1))

print("possible moves\n")
_, boards = board.returnPossibleMoves(forOpponent=True)
for  b in boards:
    print(f"shape b: y:{len(b)} x:{(len(b[0]))}")
    
    print(Board(b).display_board())



#test 8
print("\n\ntest8\n")
board = Board([
                [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  1,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  1,  0,  0,  0],
                [ 0,  0,  0,  -2,  0,  0,  0,  0],
               [ 0,  0,  1,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0]
            ])

print(board.display_board())

# print(board.get_possible_moves_for_piece(x=2, y=1))

print("possible moves\n")
_, boards = board.returnPossibleMoves(forOpponent=True)
for position_as_int_list in boards:
    print(f"shape b: y:{len(b)} x:{(len(b[0]))}")
    board_object = Board(position_as_int_list)
    print(board_object.display_board())


#test9

print("\n\ntest9\n")
board = Board([
                [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  1,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
               [ 0,  0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0,  0]
            ])

print(board.get_possible_moves_for_piece(3, 4))



