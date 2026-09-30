"""Let two chess engines play against each other.

Usage:
    python chess/main.py jonas nils
    python chess/main.py jonas nils --time 60 --increment 1 --games 4

Each argument is the name of a folder next to this file that contains an
`engine.py` with a function `get_move(state)`. See README.md.
"""

import argparse
import importlib
import threading
import time

from clock import ChessClock
from game import Game, IllegalMove


def load_engine(name):
    module = importlib.import_module(f"{name}.engine")
    return module.get_move


def ask_engine(get_move, state, timeout):
    """Call the engine in a thread so we can stop waiting when its time is up."""
    answer = {}

    def run():
        try:
            answer["move"] = get_move(state)
        except Exception as e:
            answer["error"] = e

    thread = threading.Thread(target=run, daemon=True)
    start = time.perf_counter()
    thread.start()
    thread.join(timeout)
    return answer, time.perf_counter() - start


def play_game(engines, names, seconds, increment, verbose=True):
    """Play one game. engines/names are dicts keyed by "w" and "b". Returns (score, reason)."""
    game = Game()
    clock = ChessClock(seconds, increment)

    def lose(color, reason):
        return ("0-1" if color == "w" else "1-0"), f"{names[color]} {reason}"

    if verbose:
        print(game, "\n")

    while True:
        result = game.result()
        if result:
            return result

        color = game.turn
        opponent = "b" if color == "w" else "w"
        state = game.state()
        state["time_left"] = clock.time_left(color)
        state["opponent_time_left"] = clock.time_left(opponent)

        answer, elapsed = ask_engine(engines[color], state, clock.time_left(color))

        if not clock.charge(color, elapsed) or not answer:
            if game.has_only_king(opponent):
                return "1/2-1/2", f"{names[color]} ran out of time, but {names[opponent]} can't mate"
            return lose(color, "ran out of time")
        if "error" in answer:
            return lose(color, f"crashed: {answer['error']!r}")

        move = answer["move"]
        try:
            game.play(move)
        except IllegalMove as e:
            return lose(color, f"played an illegal move {move!r}: {e}")

        if verbose:
            number = f"{state['fullmove_number']}." + ("" if color == "w" else "..")
            print(f"{number} {names[color]}: {move}   "
                  f"(took {elapsed:.2f}s, clock w {clock.time_left('w'):.1f}s / b {clock.time_left('b'):.1f}s)")
            print(game, "\n")


def main():
    parser = argparse.ArgumentParser(description="Let two chess engines play against each other.")
    parser.add_argument("player1", help="folder of the first engine (plays white in game 1)")
    parser.add_argument("player2", help="folder of the second engine")
    parser.add_argument("--time", type=float, default=300, help="seconds per player per game (default 300)")
    parser.add_argument("--increment", type=float, default=0, help="seconds added after each move (default 0)")
    parser.add_argument("--games", type=int, default=1, help="number of games, colors alternate (default 1)")
    parser.add_argument("--quiet", action="store_true", help="only print the results")
    args = parser.parse_args()

    players = [args.player1, args.player2]
    engines = {name: load_engine(name) for name in players}
    score = {name: 0.0 for name in players}

    for i in range(args.games):
        white, black = players if i % 2 == 0 else players[::-1]
        print(f"=== Game {i + 1}: {white} (white) vs {black} (black) ===")
        result, reason = play_game(
            {"w": engines[white], "b": engines[black]},
            {"w": white, "b": black},
            args.time, args.increment, verbose=not args.quiet,
        )
        points = {"1-0": (1, 0), "0-1": (0, 1), "1/2-1/2": (0.5, 0.5)}[result]
        score[white] += points[0]
        score[black] += points[1]
        print(f"Result: {result} ({reason})\n")

    if args.games > 1:
        print("=== Final score ===")
        for name in players:
            print(f"{name}: {score[name]}")


if __name__ == "__main__":
    main()
