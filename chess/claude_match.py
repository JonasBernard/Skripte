"""Judge for a game between a Claude Code session and one of the Python engines.

Claude plays by running this script once per move:

    python chess/claude_match.py new jonas --claude-color black
    python chess/claude_match.py move Nf3
    python chess/claude_match.py status
    python chess/claude_match.py resign

The game is saved in chess/claude_match.json between commands. Whenever it is
the engine's turn, the judge runs the engine right away, so every command ends
with Claude to move or with the game over. Finished games are saved as PGN in
chess/games/.

Claude's clock runs from the moment the judge prints a position until the next
`move` command arrives. The engine is loaded fresh for every move, so it can't
keep anything in memory between moves in this mode.
"""

import argparse
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from clock import ChessClock
from game import Game, IllegalMove, other, square_name
from main import ask_engine, load_engine

HERE = Path(__file__).parent
STATE_FILE = HERE / "claude_match.json"
GAMES_DIR = HERE / "games"
COLOR = {"w": "White", "b": "Black"}
COMMAND = "python chess/claude_match.py"


# ---------- state ----------

def load_state():
    if not STATE_FILE.exists():
        sys.exit(f"No game running. Start one with: {COMMAND} new <engine>")
    return json.loads(STATE_FILE.read_text())


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def restore(state):
    game = Game()
    for move in state["moves"]:
        game.play(move)
    clock = ChessClock(0, state["increment"])
    clock.remaining = dict(state["clock"])
    return game, clock


def name(state, color):
    return "Claude" if color == state["claude_color"] else state["engine"]


# ---------- output ----------

def fmt_time(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"


def movetext(sans):
    parts = []
    for i, san in enumerate(sans):
        parts.append(f"{i // 2 + 1}. {san}" if i % 2 == 0 else san)
    return " ".join(parts)


def piece_list(game, color):
    order = "KQRBNP"
    pieces = []
    for rank in range(8):
        for file in range(8):
            p = game.board[rank][file]
            if p != "." and (p.isupper() == (color == "w")):
                pieces.append((order.index(p.upper()), p.upper(), square_name((rank, file))))
    return ", ".join(kind + square for _, kind, square in sorted(pieces))


def diagram(game):
    lines = ["    a b c d e f g h", "  +-----------------+"]
    for rank in range(7, -1, -1):
        lines.append(f"{rank + 1} | " + " ".join(game.board[rank]) + f" | {rank + 1}")
    lines += ["  +-----------------+", "    a b c d e f g h"]
    return "\n".join(lines)


def show(state, game, clock, note=None):
    me = state["claude_color"]
    engine = state["engine"]
    out = []
    if note:
        out += [note, ""]
    sans = state["san"]
    if sans and len(sans) % 2 == (0 if me == "w" else 1):
        i = len(sans) - 1
        number = f"{i // 2 + 1}." + ("" if i % 2 == 0 else "..")
        out.append(f"{engine} ({COLOR[other(me)]}) played {number} {sans[-1]}  [{state['moves'][-1]}]")
        out.append("")
    out.append(diagram(game))
    out.append("Uppercase = White, lowercase = Black, '.' = empty square.")
    out.append("")
    out.append(f"White: {piece_list(game, 'w')}")
    out.append(f"Black: {piece_list(game, 'b')}")
    out.append(f"FEN:   {game.fen()}")
    out.append(f"Moves: {movetext(sans) or '(none yet)'}")
    out.append("")
    out.append(f"Clock: Claude ({COLOR[me]}) {fmt_time(clock.time_left(me))}, "
               f"{engine} ({COLOR[other(me)]}) {fmt_time(clock.time_left(other(me)))}")
    out.append(f"Rejected moves: {state['strikes']} of {state['strike_limit']} allowed")
    if state["result"]:
        return print("\n".join(out))
    if game.in_check(me):
        out.append("You are in check.")
    out.append("")
    out.append(f"Your move as {COLOR[me]} (move {game.fullmove}). Your clock is running. Submit with:")
    out.append(f"  {COMMAND} move <move>      e.g. Nf3, exd5, O-O, e8=Q (SAN) or g1f3 (UCI)")
    print("\n".join(out))


# ---------- game flow ----------

def finish(state, game, clock, result, reason):
    state["result"] = [result, reason]
    save_state(state)

    tags = {
        "Event": f"Claude vs {state['engine']}",
        "Date": datetime.now().strftime("%Y.%m.%d"),
        "White": name(state, "w"),
        "Black": name(state, "b"),
        "Result": result,
        "Termination": reason,
    }
    pgn = "\n".join(f'[{k} "{v}"]' for k, v in tags.items()) + f"\n\n{movetext(state['san'])} {result}\n"
    GAMES_DIR.mkdir(exist_ok=True)
    path = GAMES_DIR / f"{datetime.now():%Y-%m-%d_%H%M%S}_{tags['White']}-vs-{tags['Black']}.pgn"
    path.write_text(pgn)

    if result == "1/2-1/2":
        verdict = "Draw"
    else:
        verdict = f"{name(state, 'w' if result == '1-0' else 'b')} wins"
    show(state, game, clock, f"GAME OVER: {result}. {verdict} ({reason}).")
    print(f"\nPGN saved to {path.relative_to(HERE.parent)}")


def lose(state, game, clock, color, reason):
    finish(state, game, clock, "0-1" if color == "w" else "1-0", f"{name(state, color)} {reason}")


def flag(state, game, clock, color):
    """`color` ran out of time."""
    clock.remaining[color] = 0.0
    state["clock"] = clock.remaining
    if game.has_only_king(other(color)):
        return finish(state, game, clock, "1/2-1/2",
                      f"{name(state, color)} ran out of time, but {name(state, other(color))} can't mate")
    lose(state, game, clock, color, "ran out of time")


def continue_game(state, game, clock, note=None):
    """Let the engine move if it's its turn, then hand the position to Claude."""
    result = game.result()
    if not result and game.turn != state["claude_color"]:
        color = game.turn
        engine_state = game.state()
        engine_state["time_left"] = clock.time_left(color)
        engine_state["opponent_time_left"] = clock.time_left(other(color))
        answer, elapsed = ask_engine(load_engine(state["engine"]), engine_state, clock.time_left(color))

        if not clock.charge(color, elapsed) or not answer:
            return flag(state, game, clock, color)
        state["clock"] = clock.remaining
        if "error" in answer:
            return lose(state, game, clock, color, f"crashed: {answer['error']!r}")
        try:
            san = game.play(answer["move"])
        except IllegalMove as e:
            return lose(state, game, clock, color, f"played an illegal move {answer['move']!r}: {e}")
        state["moves"].append(game.moves[-1])
        state["san"].append(san)
        result = game.result()

    if result:
        return finish(state, game, clock, *result)
    state["turn_started"] = time.time()
    save_state(state)
    show(state, game, clock, note)


def cmd_new(args):
    if STATE_FILE.exists() and not load_state()["result"] and not args.force:
        sys.exit(f"A game is still running. Continue it with `{COMMAND} status`, or start over with --force.")
    try:
        load_engine(args.engine)
    except Exception as e:
        sys.exit(f"Can't load engine {args.engine!r}: {e!r}")

    color = args.claude_color
    if color == "random":
        color = random.choice(["white", "black"])
    me = color[0]
    state = {
        "engine": args.engine,
        "claude_color": me,
        "moves": [],
        "san": [],
        "clock": {me: float(args.claude_time), other(me): float(args.engine_time)},
        "increment": args.increment,
        "strikes": 0,
        "strike_limit": args.strikes,
        "turn_started": time.time(),
        "result": None,
    }
    game, clock = restore(state)
    print(f"New game: Claude plays {COLOR[me]}, {args.engine} plays {COLOR[other(me)]}.\n")
    continue_game(state, game, clock)


def running_game():
    state = load_state()
    game, clock = restore(state)
    if state["result"]:
        show(state, game, clock, f"This game is over: {state['result'][0]} ({state['result'][1]}).")
        sys.exit(0)
    return state, game, clock


def cmd_move(args):
    state, game, clock = running_game()
    me = state["claude_color"]
    elapsed = time.time() - state["turn_started"]
    if elapsed >= clock.time_left(me):
        return flag(state, game, clock, me)

    try:
        move = game.find_move(args.move)
    except IllegalMove as e:
        state["strikes"] += 1
        if state["strikes"] >= state["strike_limit"]:
            return lose(state, game, clock, me, f"made {state['strikes']} illegal moves (last: {e})")
        save_state(state)  # the clock keeps running from turn_started
        clock.remaining[me] -= elapsed
        return show(state, game, clock, f"REJECTED: {e}. Your clock is still running, try again.")

    clock.charge(me, elapsed)
    state["clock"] = clock.remaining
    state["san"].append(game.play(move))
    state["moves"].append(game.moves[-1])
    continue_game(state, game, clock, f"You played {state['san'][-1]}  [{move}]")


def cmd_status(args):
    state, game, clock = running_game()
    me = state["claude_color"]
    elapsed = time.time() - state["turn_started"]
    if elapsed >= clock.time_left(me):
        return flag(state, game, clock, me)
    clock.remaining[me] -= elapsed
    show(state, game, clock)


def cmd_resign(args):
    state, game, clock = running_game()
    lose(state, game, clock, state["claude_color"], "resigned")


def main():
    parser = argparse.ArgumentParser(description="Play chess as Claude against one of the Python engines.")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="start a new game")
    new.add_argument("engine", help="folder of the engine to play against, e.g. jonas")
    new.add_argument("--claude-color", choices=["white", "black", "random"], default="random")
    new.add_argument("--claude-time", type=float, default=3600, help="Claude's seconds for the game (default 3600)")
    new.add_argument("--engine-time", type=float, default=300, help="the engine's seconds for the game (default 300)")
    new.add_argument("--increment", type=float, default=0, help="seconds added after each move (default 0)")
    new.add_argument("--strikes", type=int, default=3, help="rejected moves allowed before Claude loses (default 3)")
    new.add_argument("--force", action="store_true", help="abandon a running game")
    new.set_defaults(func=cmd_new)

    move = sub.add_parser("move", help="play a move, e.g. Nf3 or g1f3")
    move.add_argument("move")
    move.set_defaults(func=cmd_move)

    sub.add_parser("status", help="show the current position").set_defaults(func=cmd_status)
    sub.add_parser("resign", help="give up the game").set_defaults(func=cmd_resign)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
