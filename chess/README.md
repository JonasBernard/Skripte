# Chess engine competition

Two engines, one game. `main.py` runs the game, `game.py` knows the rules, `clock.py` keeps time.
Each player writes their engine in their own folder (`jonas/`, `nils/`).

```
python chess/main.py jonas nils                                   # one game, 5 minutes each
python chess/main.py jonas nils --time 60 --increment 1 --games 10 --quiet
```

With `--games`, the colors alternate and the final score is printed at the end.

## Writing an engine

Put a file `engine.py` in your folder with one function:

```python
def get_move(state):
    return "e2e4"
```

`state` is a dict with the current position and nothing else. You don't get a list of legal moves.
You have to work that out yourself:

| key | meaning |
|---|---|
| `board` | 8x8 list, `board[rank][file]`. `board[0][0]` is a1, `board[1][4]` is e2. White `PNBRQK`, black `pnbrqk`, empty `.` |
| `turn` | `"w"` or `"b"`, the color you are playing |
| `castling` | castling rights still left, e.g. `"KQkq"`, or `""` |
| `en_passant` | the square you could capture en passant onto, e.g. `"e3"`, or `None` |
| `halfmove_clock` | half-moves since the last capture or pawn move (draw at 100) |
| `fullmove_number` | starts at 1, goes up after black moves |
| `fen` | the same position as a [FEN](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) string |
| `time_left` / `opponent_time_left` | seconds left on the clocks |

Return the move in UCI notation: `"g1f3"`, castling as the king move `"e1g1"`, promotion with a suffix `"e7e8n"`
(without a suffix it promotes to a queen).

You can split your engine into more files in your folder and import them with `from . import helper`.

## Rules

- You lose if you return an illegal move, raise an exception or run out of time. The clock runs while `get_move` is thinking.
- If you run out of time and your opponent only has a king left, it's a draw.
- Draws: stalemate, 50-move rule, threefold repetition, insufficient material (only K vs K, K+B vs K, K+N vs K).
- Fair play: don't import `game.py` or anything from the other player's folder, and don't dig around in the running
  program. Your engine only gets to use `state`.

The placeholder engines ask for moves on the keyboard, so you can play against each other while you're still building.
