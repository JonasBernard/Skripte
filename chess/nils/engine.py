"""Nils' chess engine.

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


def get_move(state):
    return input(f"{'White' if state['turn'] == 'w' else 'Black'} to move: ")
