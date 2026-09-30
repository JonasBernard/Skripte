"""Test exactly one Jonas-engine move from a random reachable position."""

import random

from game import Game, uci
from jonas.engine import get_move


def random_position(rng):
    for _ in range(100):
        game = Game()
        for _ in range(rng.randint(2, 10)):
            legal_moves = game.legal_moves()
            if not legal_moves:
                break
            game.play(uci(rng.choice(legal_moves)))

        before = game.state()
        move = get_move(before)
        if move is None:
            continue
        try:
            san = game.play(move)
        except Exception:
            continue
        return before, game, move, san

    raise RuntimeError("Konnte keinen legalen Jonas-Zug finden.")


def main():
    before, game, move, san = random_position(random.Random())
    print("Ausgangsposition:")
    print(Game(before["fen"]))
    print()
    print(f"Jonas spielt: {move} ({san})")
    print()
    print("Brett nach dem Zug:")
    print(game)


if __name__ == "__main__":
    main()