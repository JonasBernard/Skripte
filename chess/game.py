"""Chess rules: board state, move validation and game end detection.

The board is a list of 8 rows, board[rank][file], where rank 0 is rank "1"
(white's back rank) and file 0 is the a-file. So "e2" is board[1][4].
White pieces are uppercase (PNBRQK), black pieces lowercase, empty squares ".".
"""

FILES = "abcdefgh"
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

KNIGHT_STEPS = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
KING_STEPS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
ROOK_DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
BISHOP_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


class IllegalMove(Exception):
    pass


def parse_square(name):
    if len(name) != 2 or name[0] not in FILES or name[1] not in "12345678":
        raise ValueError(f"not a square: {name!r}")
    return int(name[1]) - 1, FILES.index(name[0])


def square_name(square):
    rank, file = square
    return f"{FILES[file]}{rank + 1}"


def uci(move):
    start, target, promo = move
    return square_name(start) + square_name(target) + (promo or "")


def color_of(piece):
    if piece == ".":
        return None
    return "w" if piece.isupper() else "b"


def other(color):
    return "b" if color == "w" else "w"


def on_board(rank, file):
    return 0 <= rank < 8 and 0 <= file < 8


def piece_of(color, kind):
    return kind.upper() if color == "w" else kind.lower()


class Game:
    def __init__(self, fen=START_FEN):
        self._load_fen(fen)
        self.moves = []
        self.repetitions = {self._position_key(): 1}

    # ---------- setup / export ----------

    def _load_fen(self, fen):
        placement, turn, castling, ep, halfmove, fullmove = fen.split()
        self.board = [["."] * 8 for _ in range(8)]
        for i, row in enumerate(placement.split("/")):
            rank = 7 - i
            file = 0
            for ch in row:
                if ch.isdigit():
                    file += int(ch)
                else:
                    self.board[rank][file] = ch
                    file += 1
        self.turn = turn
        self.castling = "" if castling == "-" else castling
        self.ep = None if ep == "-" else parse_square(ep)
        self.halfmove = int(halfmove)
        self.fullmove = int(fullmove)

    def _placement(self):
        rows = []
        for rank in range(7, -1, -1):
            row, empty = "", 0
            for piece in self.board[rank]:
                if piece == ".":
                    empty += 1
                else:
                    row += (str(empty) if empty else "") + piece
                    empty = 0
            rows.append(row + (str(empty) if empty else ""))
        return "/".join(rows)

    def fen(self):
        ep = square_name(self.ep) if self.ep else "-"
        return f"{self._placement()} {self.turn} {self.castling or '-'} {ep} {self.halfmove} {self.fullmove}"

    def state(self):
        """Read-only snapshot of the position. This is all an engine gets to see."""
        return {
            "board": [row[:] for row in self.board],
            "turn": self.turn,
            "castling": self.castling,
            "en_passant": square_name(self.ep) if self.ep else None,
            "halfmove_clock": self.halfmove,
            "fullmove_number": self.fullmove,
            "fen": self.fen(),
        }

    def __str__(self):
        lines = []
        for rank in range(7, -1, -1):
            lines.append(f"{rank + 1}  " + " ".join(self.board[rank]))
        lines.append("   " + " ".join(FILES))
        return "\n".join(lines)

    def _copy(self):
        game = Game.__new__(Game)
        game.board = [row[:] for row in self.board]
        game.turn = self.turn
        game.castling = self.castling
        game.ep = self.ep
        game.halfmove = self.halfmove
        game.fullmove = self.fullmove
        return game

    # ---------- attacks ----------

    def is_attacked(self, square, by):
        rank, file = square
        board = self.board

        # a pawn of colour `by` attacks diagonally forward
        forward = 1 if by == "w" else -1
        for df in (-1, 1):
            r, f = rank - forward, file + df
            if on_board(r, f) and board[r][f] == piece_of(by, "P"):
                return True

        for steps, kind in ((KNIGHT_STEPS, "N"), (KING_STEPS, "K")):
            for dr, df in steps:
                r, f = rank + dr, file + df
                if on_board(r, f) and board[r][f] == piece_of(by, kind):
                    return True

        for dirs, kinds in ((ROOK_DIRS, "RQ"), (BISHOP_DIRS, "BQ")):
            attackers = {piece_of(by, k) for k in kinds}
            for dr, df in dirs:
                r, f = rank + dr, file + df
                while on_board(r, f):
                    if board[r][f] != ".":
                        if board[r][f] in attackers:
                            return True
                        break
                    r, f = r + dr, f + df
        return False

    def in_check(self, color):
        king = piece_of(color, "K")
        for rank in range(8):
            for file in range(8):
                if self.board[rank][file] == king:
                    return self.is_attacked((rank, file), other(color))
        return False

    # ---------- move generation (internal, engines don't get this) ----------

    def _pseudo_moves(self, color):
        """Moves that follow piece movement rules, ignoring whether the own king is left in check."""
        board = self.board
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if color_of(piece) != color:
                    continue
                kind = piece.upper()
                start = (rank, file)

                if kind == "P":
                    yield from self._pawn_moves(start, color)
                elif kind in "NK":
                    for dr, df in KNIGHT_STEPS if kind == "N" else KING_STEPS:
                        r, f = rank + dr, file + df
                        if on_board(r, f) and color_of(board[r][f]) != color:
                            yield start, (r, f), None
                    if kind == "K":
                        yield from self._castling_moves(start, color)
                else:
                    dirs = {"R": ROOK_DIRS, "B": BISHOP_DIRS, "Q": ROOK_DIRS + BISHOP_DIRS}[kind]
                    for dr, df in dirs:
                        r, f = rank + dr, file + df
                        while on_board(r, f):
                            if color_of(board[r][f]) == color:
                                break
                            yield start, (r, f), None
                            if board[r][f] != ".":
                                break
                            r, f = r + dr, f + df

    def _pawn_moves(self, start, color):
        board = self.board
        rank, file = start
        forward = 1 if color == "w" else -1
        start_rank = 1 if color == "w" else 6
        last_rank = 7 if color == "w" else 0

        targets = []
        r = rank + forward
        if board[r][file] == ".":
            targets.append((r, file))
            if rank == start_rank and board[r + forward][file] == ".":
                targets.append((r + forward, file))
        for df in (-1, 1):
            f = file + df
            if not on_board(r, f):
                continue
            if color_of(board[r][f]) == other(color) or (r, f) == self.ep:
                targets.append((r, f))

        for target in targets:
            if target[0] == last_rank:
                for promo in "qrbn":
                    yield start, target, promo
            else:
                yield start, target, None

    def _castling_moves(self, start, color):
        row = 0 if color == "w" else 7
        if start != (row, 4) or self.is_attacked(start, other(color)):
            return
        board = self.board
        rook = piece_of(color, "R")
        king_side, queen_side = ("K", "Q") if color == "w" else ("k", "q")
        enemy = other(color)
        if (king_side in self.castling and board[row][7] == rook
                and board[row][5] == board[row][6] == "."
                and not self.is_attacked((row, 5), enemy)):
            yield start, (row, 6), None
        if (queen_side in self.castling and board[row][0] == rook
                and board[row][1] == board[row][2] == board[row][3] == "."
                and not self.is_attacked((row, 3), enemy)):
            yield start, (row, 2), None
        # the king's target square is checked like any other move in legal_moves()

    def legal_moves(self):
        moves = []
        for move in self._pseudo_moves(self.turn):
            after = self._copy()
            after._apply(move)
            if not after.in_check(self.turn):
                moves.append(move)
        return moves

    # ---------- making moves ----------

    def _apply(self, move):
        (r1, f1), (r2, f2), promo = move
        board = self.board
        piece = board[r1][f1]
        kind = piece.upper()
        captured = board[r2][f2]

        if kind == "P" and (r2, f2) == self.ep and captured == ".":
            captured = board[r1][f2]
            board[r1][f2] = "."  # en passant

        board[r2][f2] = piece_of(self.turn, promo) if promo else piece
        board[r1][f1] = "."

        if kind == "K" and abs(f2 - f1) == 2:  # castling: move the rook too
            rook_from, rook_to = (7, 5) if f2 == 6 else (0, 3)
            board[r1][rook_to] = board[r1][rook_from]
            board[r1][rook_from] = "."

        # moving the king or a rook, or capturing a rook, removes castling rights
        for square, rights in (((0, 4), "KQ"), ((0, 7), "K"), ((0, 0), "Q"),
                               ((7, 4), "kq"), ((7, 7), "k"), ((7, 0), "q")):
            if square in ((r1, f1), (r2, f2)):
                self.castling = "".join(c for c in self.castling if c not in rights)

        self.ep = ((r1 + r2) // 2, f1) if kind == "P" and abs(r2 - r1) == 2 else None
        self.halfmove = 0 if kind == "P" or captured != "." else self.halfmove + 1
        if self.turn == "b":
            self.fullmove += 1
        self.turn = other(self.turn)

    def parse_move(self, text):
        """Parse UCI notation like "e2e4" or "e7e8q". Promotion defaults to queen."""
        if not isinstance(text, str):
            raise IllegalMove(f"move must be a string, got {type(text).__name__}")
        text = text.strip().lower()
        if len(text) not in (4, 5):
            raise IllegalMove("expected UCI notation like 'e2e4' or 'e7e8q'")
        try:
            start, target = parse_square(text[:2]), parse_square(text[2:4])
        except ValueError as e:
            raise IllegalMove(str(e))
        promo = text[4] if len(text) == 5 else None
        if promo is not None and promo not in "qrbn":
            raise IllegalMove(f"invalid promotion piece {promo!r}")
        piece = self.board[start[0]][start[1]]
        if promo is None and piece.upper() == "P" and target[0] in (0, 7):
            promo = "q"
        return start, target, promo

    def play(self, text):
        """Validate and play a move given in UCI notation. Raises IllegalMove.

        Returns the move in standard algebraic notation (SAN), e.g. "Nf3".
        """
        move = self.parse_move(text)
        start = move[0]
        piece = self.board[start[0]][start[1]]
        if piece == ".":
            raise IllegalMove(f"no piece on {square_name(start)}")
        if color_of(piece) != self.turn:
            raise IllegalMove(f"the piece on {square_name(start)} is not yours")
        legal = self.legal_moves()
        if move not in legal:
            raise IllegalMove("not a legal move in this position")
        san = self.san(move, legal)
        self._apply(move)
        self.moves.append(uci(move))
        key = self._position_key()
        self.repetitions[key] = self.repetitions.get(key, 0) + 1
        return san

    # ---------- standard algebraic notation (used by the Claude judge) ----------

    def san(self, move, legal=None, suffix=True):
        """Standard algebraic notation of a legal move: "e4", "Nbd7", "exd5", "O-O", "e8=Q+"."""
        (r1, f1), (r2, f2), promo = move
        piece = self.board[r1][f1]
        kind = piece.upper()
        if kind == "K" and abs(f2 - f1) == 2:
            text = "O-O" if f2 == 6 else "O-O-O"
        else:
            capture = self.board[r2][f2] != "." or (kind == "P" and (r2, f2) == self.ep)
            target = square_name((r2, f2))
            if kind == "P":
                text = (FILES[f1] + "x" if capture else "") + target
                if promo:
                    text += "=" + promo.upper()
            else:
                legal = self.legal_moves() if legal is None else legal
                rivals = [m[0] for m in legal
                          if m[1] == (r2, f2) and m[0] != (r1, f1) and self.board[m[0][0]][m[0][1]] == piece]
                hint = ""
                if rivals:
                    if all(f != f1 for _, f in rivals):
                        hint = FILES[f1]
                    elif all(r != r1 for r, _ in rivals):
                        hint = str(r1 + 1)
                    else:
                        hint = square_name((r1, f1))
                text = kind + hint + ("x" if capture else "") + target
        if suffix:
            after = self._copy()
            after._apply(move)
            if after.in_check(after.turn):
                text += "#" if not after.legal_moves() else "+"
        return text

    def find_move(self, text):
        """Accept a move in UCI ("g1f3") or SAN ("Nf3", "exd5", "O-O", "e8=Q"). Returns it in UCI.

        Raises IllegalMove if it doesn't match exactly one legal move.
        """
        text = text.strip()
        legal = self.legal_moves()
        try:
            move = self.parse_move(text)
            if move in legal:
                return uci(move)
        except IllegalMove:
            pass

        def normalize(s):
            return s.replace("0", "O").translate(str.maketrans("", "", "+#x=!?"))

        wanted = normalize(text)
        matches = [m for m in legal if normalize(self.san(m, legal, suffix=False)) == wanted]
        if len(matches) == 1:
            return uci(matches[0])
        if len(matches) > 1:
            raise IllegalMove(f"{text!r} is ambiguous, say which piece moves (e.g. 'Nbd7' or 'R1e2')")
        raise IllegalMove(f"{text!r} is not a legal move in this position")

    # ---------- game end ----------

    def _position_key(self):
        # the en passant square only matters if a pawn could actually capture there
        ep = "-"
        if self.ep:
            rank, file = self.ep
            pawn_rank = rank - (1 if self.turn == "w" else -1)
            pawn = piece_of(self.turn, "P")
            if any(on_board(pawn_rank, file + df) and self.board[pawn_rank][file + df] == pawn for df in (-1, 1)):
                ep = square_name(self.ep)
        return f"{self._placement()} {self.turn} {self.castling} {ep}"

    def pieces(self, color):
        return [p.upper() for row in self.board for p in row if color_of(p) == color]

    def has_only_king(self, color):
        return self.pieces(color) == ["K"]

    def _insufficient_material(self):
        others = [p for p in self.pieces("w") + self.pieces("b") if p != "K"]
        return others == [] or others in (["N"], ["B"])

    def result(self):
        """None while the game is running, else (score, reason), e.g. ("1-0", "checkmate")."""
        if not self.legal_moves():
            if self.in_check(self.turn):
                return ("0-1" if self.turn == "w" else "1-0"), "checkmate"
            return "1/2-1/2", "stalemate"
        if self.halfmove >= 100:
            return "1/2-1/2", "50-move rule"
        if self.repetitions[self._position_key()] >= 3:
            return "1/2-1/2", "threefold repetition"
        if self._insufficient_material():
            return "1/2-1/2", "insufficient material"
        return None
