---
name: play-chess
description: Play a game of chess against one of the Python engines in chess/ (for example "play chess against jonas"). Use when the user asks you to play chess against an engine in this repository.
allowed-tools: Bash(python chess/claude_match.py:*), Bash(python3 chess/claude_match.py:*)
---

# Play chess against a Python engine

You are playing a game of chess against an engine that a person in this repository wrote.
The judge `chess/claude_match.py` keeps the game, checks your moves, runs the engine and runs both clocks.
The user tells you which engine to play (the name of its folder in `chess/`, e.g. `jonas`) and may pick your color
or time control. Arguments: $ARGUMENTS

## How to play

1. Start the game (add `--claude-color white` or `black` if the user asked for a color):
   ```
   python chess/claude_match.py new <engine>
   ```
2. The judge prints the position: the engine's last move, a board diagram (White at the bottom, uppercase = White),
   a piece list for each side, the FEN, the moves so far, the clocks and how many of your moves were rejected.
3. Pick your move and submit it:
   ```
   python chess/claude_match.py move <move>
   ```
   Use SAN (`Nf3`, `exd5`, `O-O`, `O-O-O`, `e8=Q`, `Rad1`) or UCI (`g1f3`). The judge plays your move,
   lets the engine answer, and prints the next position.
4. Repeat until the judge prints `GAME OVER`. Then tell the user the result, how it ended, and where the PGN was saved.

`python chess/claude_match.py status` shows the position again. `python chess/claude_match.py resign` resigns.

## Rules

- Play the whole game without stopping to ask the user anything, unless the judge reports an error you can't handle.
- Choose every move by your own thinking about the position the judge prints. Don't run any code to find or check
  moves: no chess libraries or engines, no analysis scripts, don't import `chess/game.py`.
- Only use the judge's output. Don't read the engine's folder, `chess/game.py`, `chess/main.py` or
  `chess/claude_match.json`.
- Your clock runs from the moment the judge prints the position until your next `move` command.
  Think carefully but don't dawdle, and keep an eye on the clock line.
- A move the judge rejects counts against you. After 3 rejected moves you lose, so before submitting check that
  your piece really stands on the square you think, that its path is clear, and that your king isn't left in check.

## Before each move

- What did the engine's last move do? Does it attack something, threaten mate or leave something undefended?
- Are any of your pieces hanging? Is your king safe?
- Look at checks, captures and threats for both sides before quieter moves.
- Write down your move and a sentence of reasoning, then submit it.
