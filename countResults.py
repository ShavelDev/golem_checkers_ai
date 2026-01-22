import pickle
from pathlib import Path



folder_z_grami = "/Users/norbert/Projects/golem/golem_checkers_ai/training_games"


games = []
player1_wins = 0
player1_depth = -1
player2_wins = 0
player2_depth = -1
for pkl_file in Path(f'{folder_z_grami}').glob('*.pkl'):
    with open(pkl_file, 'rb') as f:
        game = pickle.load(f)
        games.append(game)
        if player1_depth == -1:

            player1_depth = game['player1_depth']
        if player2_depth == -1:
            player2_depth = game['player2_depth']
        if game['player1_depth'] != player1_depth:
            print("wykryto zmiane w glebokosci minmaxa dla gracza 1 dla tego gracza")
            print("Gaju chyba wymieszalas pliki xd")
        if game['player2_depth'] != player2_depth:
            print("wykryto zmiane w glebokosci minmaxa dla gracza 2 dla tego gracza")
            print("Gaju chyba wymieszalas pliki xd")
        print(game['winner'])
        if game['winner'] == 1:
            player1_wins += 1
        elif game['winner'] == -1:
            player2_wins += 1


        

if len(games) != 0:
    total_games = len(games)
    print(f'Gracz1: {player1_depth}, Gracz2: {player2_depth}')
    print('----------- BEZ REMISOW -----------')
    print(f"Gry wygrane przez gracza 1: {player1_wins} w % {player1_wins/(player1_wins+player2_wins) * 100}%")
    print(f"Gry wygrane przez gracza 2:  {player2_wins} w % {player2_wins/(player1_wins+player2_wins) * 100}%")
    print('----------- Z REMISAMI -----------')
    print(f"Gry wygrane przez gracza 1: {player1_wins} w % {player1_wins/total_games * 100}%")
    print(f"Gry wygrane przez gracza 2: {player2_wins}  w % {player2_wins/total_games * 100}%")
    print(f"Gry zremisowane: {total_games - player1_wins - player2_wins} w %: {(total_games - player1_wins - player2_wins)/total_games* 100}%")
    print("")
