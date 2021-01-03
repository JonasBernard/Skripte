def symbol(board, index):
    return index + 1 if board[index] == 0 else "X" if board[index] == 1 else "0"


def print_board(board):
    print("-------------------")
    print(f"|  {symbol(board, 0)}  |  {symbol(board, 1)}  |  {symbol(board, 2)}  |")
    print("-------------------")
    print(f"|  {symbol(board, 3)}  |  {symbol(board, 4)}  |  {symbol(board, 5)}  |")
    print("-------------------")
    print(f"|  {symbol(board, 6)}  |  {symbol(board, 7)}  |  {symbol(board, 8)}  |")
    print("-------------------")


possible_wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]


def is_completed(board):
    for field in board:
        if field == 0:
            return False
    return True


def winner(board):
    if is_completed(board):
        return 0
    for win in possible_wins:
        if board[win[0]] == board[win[1]] and board[win[1]] == board[win[2]] and board[win[0]] != 0:
            return board[win[0]]
    return None


def computermove(board, moves):
    if moves == 0:
        if board[4] == 0:
            board[4] = -1
        else:
            board[0] = -1
        return board
    else:
        i = 0
        while board[i] != 0:
            i += 1
        board[i] = -1
    return board


rows = 3
cols = 3
print("---------------------------------------------------")
print("|         Willkommen zu Tic Tac Toe               |")
print("---------------------------------------------------")
play_on = True
score = 0
while play_on:
    board = [0 for x in range(rows * cols)]
    moves = 0
    print("Okay. Lass uns eine Runde Spielen. Du fängst an:")
    won = None
    while won is None:
        print_board(board)
        possible_fields = [f"{i + 1}" for i in (filter(lambda i: board[i] == 0, range(9)))]
        field = input(f"Auf welches Feld willst du setzen? (1-9)")
        while field not in possible_fields:
            field = input("Bitte gib die Nummer für ein Feld ein, welches noch nicht besetzt ist. "
                          f"Auf welches Feld willst du setzen? (" + ", ".join(possible_fields) + ")")
        board[int(field) - 1] = 1
        board = computermove(board, moves)
        moves += 1
        won = winner(board)
    if won == 1:
        score += 1
    print("--------------------------------")
    print("|          Tie game!           |" if won == 0 else
          "|          You won!            |" if won == 1 else
          "|        Computer won!         |")
    print("--------------------------------")
    print_board(board)
    play_on = input("Willst du noch eine Runde Spielen? (Ja/Nein)") == "Ja"
print("Okay. Bis zum nächsten Mal!")
print("")
print(f"Du hast {score} Mal gewonnen.")
