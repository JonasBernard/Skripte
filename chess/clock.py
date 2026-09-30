"""A simple chess clock with optional increment (Fischer)."""


class ChessClock:
    def __init__(self, seconds, increment=0.0):
        self.remaining = {"w": float(seconds), "b": float(seconds)}
        self.increment = increment

    def time_left(self, color):
        return self.remaining[color]

    def charge(self, color, elapsed):
        """Subtract the thinking time of a move. Returns False if the flag fell."""
        self.remaining[color] -= elapsed
        if self.remaining[color] <= 0:
            self.remaining[color] = 0.0
            return False
        self.remaining[color] += self.increment
        return True
