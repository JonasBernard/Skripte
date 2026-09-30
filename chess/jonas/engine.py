"""Jonas' chess engine.

get_move(state) receives a dict describing the current position and must
return a move in UCI notation: "e2e4", "g1f3", castling as the king move
("e1g1"), promotion with a suffix ("e7e8q", "a2a1n").

state = {
    "board": 8x8 list, board[rank][file], board[0] is rank 1, board[0][0] is a1.
             White pieces "PNBRQK", black pieces "pnbrqk", empty squares ".".
    "turn": "w" or "b" (the color you are playing this move),
    "castling": castling rights still available, e.g. "KQkq" or "" ,
    "en_passant": square behind a pawn that just moved two steps, e.g. "e3", or None,
    "halfmove_clock": moves since the last capture or pawn move (draw at 100),
    "fullmove_number": starts at 1, goes up after black moves,
    "fen": the same position as a FEN string,
    "moves": every move of the game so far in UCI notation, oldest first, e.g. ["e2e4", "e7e5"],
    "positions": FEN of every position so far, starting with the initial one;
                 positions[-1] is the current position (useful to spot repetitions),
    "time_left": your remaining seconds,
    "opponent_time_left": your opponent's remaining seconds,
}

An illegal move, an exception or running out of time loses the game.
This placeholder just asks a human for the move.
"""

movepatterns={
    "p": [(1,0)],
    "n": [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)],
    "b": [(1,1),(1,-1),(-1,1),(-1,-1)],
    "r": [(1,0),(-1,0),(0,1),(0,-1)],
    "q": [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)],
    "k": [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
}
lengths = {
    "p": 1,
    "n": 1,
    "b": 7,
    "r": 7,
    "q": 7,
    "k": 1
}

def get_move(state):
    board = state["board"]
    turn = state["turn"]
    my = ["P", "N", "B", "R", "Q", "K"] if turn == "w" else ["p", "n", "b", "r", "q", "k"]
    moves = []
    for piecetype in my:
        positions = find_all(piecetype, board)
        for piecepos in positions:
            piecetype = piecetype.lower()
            for dx, dy in movepatterns[piecetype]:
                for i in range(1, lengths[piecetype] + 1):
                    newpos = (piecepos[0] + dx * i, piecepos[1] + dy * i)
                    if not (0 <= newpos[0] < 8 and 0 <= newpos[1] < 8):
                        break
                    target = board[newpos[0]][newpos[1]]
                    if target == ".":
                        moves.append((piecepos, newpos))
                    elif (turn == "w" and target.islower()) or (turn == "b" and target.isupper()):
                        moves.append((piecepos, newpos))
                        break
                    else:
                        break
    if not moves:
        return None
    
    level = 2  # depth of minimax search
    # minimax up to level
    best_move = None
    best_eval = float('-inf') if turn == "w" else float('inf')
    for move in moves:
        new_board = [row[:] for row in board]
        from_pos, to_pos = move
        piece = new_board[from_pos[0]][from_pos[1]]
        new_board[to_pos[0]][to_pos[1]] = piece
        new_board[from_pos[0]][from_pos[1]] = "."
        new_state = state.copy()
        new_state["board"] = new_board
        new_state["turn"] = "b" if turn == "w" else "w"
        eval_score = minimax(new_state, level - 1, float('-inf'), float('inf'), turn == "b")
        if (turn == "w" and eval_score > best_eval) or (turn == "b" and eval_score < best_eval):
            best_eval = eval_score
            best_move = move
    return pos_to_uci(best_move[0]) + pos_to_uci(best_move[1])

def minimax(state, depth, alpha, beta, maximizing_player):
    if depth == 0:
        return eval_state(state)
    
    board = state["board"]
    turn = state["turn"]
    my = ["P", "N", "B", "R", "Q", "K"] if turn == "w" else ["p", "n", "b", "r", "q", "k"]
    moves = []
    for piecetype in my:
        positions = find_all(piecetype, board)
        for piecepos in positions:
            piecetype = piecetype.lower()
            for dx, dy in movepatterns[piecetype]:
                for i in range(1, lengths[piecetype] + 1):
                    newpos = (piecepos[0] + dx * i, piecepos[1] + dy * i)
                    if not (0 <= newpos[0] < 8 and 0 <= newpos[1] < 8):
                        break
                    target = board[newpos[0]][newpos[1]]
                    if target == ".":
                        moves.append((piecepos, newpos))
                    elif (turn == "w" and target.islower()) or (turn == "b" and target.isupper()):
                        moves.append((piecepos, newpos))
                        break
                    else:
                        break
    
    if maximizing_player:
        max_eval = float('-inf')
        for move in moves:
            new_board = [row[:] for row in board]
            from_pos, to_pos = move
            piece = new_board[from_pos[0]][from_pos[1]]
            new_board[to_pos[0]][to_pos[1]] = piece
            new_board[from_pos[0]][from_pos[1]] = "."
            new_state = state.copy()
            new_state["board"] = new_board
            new_state["turn"] = "b" if turn == "w" else "w"
            eval_score = minimax(new_state, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            new_board = [row[:] for row in board]
            from_pos, to_pos = move
            piece = new_board[from_pos[0]][from_pos[1]]
            new_board[to_pos[0]][to_pos[1]] = piece
            new_board[from_pos[0]][from_pos[1]] = "."
            new_state = state.copy()
            new_state["board"] = new_board
            new_state["turn"] = "b" if turn == "w" else "w"
            eval_score = minimax(new_state, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def find_all(piecetype, board):
    pos = []
    for rank in range(8):
        for file in range(8):
            if board[rank][file] == piecetype:
                pos.append((rank, file))

    return pos

def pos_to_uci(pos):
    return chr(pos[1] + ord('a')) + str(pos[0] + 1)

piece_values = {
    "p": 1,
    "n": 3,
    "b": 3,
    "r": 4.5,
    "q": 8.5,
    "k": 0
}

def eval_state(state):
    ev = 0

    for rank in range(8):
        for file in range(8):
            piece = state["board"][rank][file]
            if piece == ".":
                continue
            value = piece_values[piece.lower()]
            if piece.isupper():
                ev += value
            else:
                ev -= value
    return ev
