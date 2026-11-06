class board:
    def __init__(self):
        self.grid = "." * 9

    def display(self):
        for row in range(3):
            print(" | ".join(self.grid[row * 3:(row + 1) * 3]))
            print("-" * 9)

    def restart(self):
        self.grid = "." * 9

    def available_moves(self):
        return [
            divmod(index, 3)
            for index, cell in enumerate(self.grid)
            if cell == "."
        ]

    def make_move(self, pos, mark):
        row, col = pos
        if (
            0 <= row < 3
            and 0 <= col < 3
            and mark in ("X", "O")
            and self.grid[row * 3 + col] == "."
        ):
            index = row * 3 + col
            self.grid = self.grid[:index] + mark + self.grid[index + 1:]
            return True
        return False

    def winner(self):
        lines = (
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6),
        )
        for first, second, third in lines:
            mark = self.grid[first]
            if mark != "." and mark == self.grid[second] == self.grid[third]:
                return mark
        return None

    def is_full(self):
        return "." not in self.grid

    def is_over(self):
        return self.winner() is not None or self.is_full()

    def to_key(self):
        return self.grid
