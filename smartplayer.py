import random


class smartplayer:
    def __init__(self, symbol):
        self.symbol = symbol
        self.opponent_symbol = "X" if symbol == "O" else "O"

    def choose_move(self, board_state):
        moves = [index for index, cell in enumerate(board_state) if cell == "."]
        if not moves:
            return None

        scored_moves = [
            (self._score(self._play(board_state, move, self.symbol), True, 1), move)
            for move in moves
        ]
        best_score = max(score for score, _ in scored_moves)
        best_moves = [move for score, move in scored_moves if score == best_score]
        return random.choice(best_moves)

    def _play(self, state, move, symbol):
        return state[:move] + symbol + state[move + 1:]

    def _score(self, state, is_opponent_turn, depth):
        winner = self._winner(state)
        if winner == self.symbol:
            return 10 - depth
        if winner == self.opponent_symbol:
            return depth - 10
        if "." not in state:
            return 0

        next_symbol = self.opponent_symbol if is_opponent_turn else self.symbol
        scores = []
        for index, cell in enumerate(state):
            if cell == ".":
                next_state = state[:index] + next_symbol + state[index + 1:]
                scores.append(self._score(next_state, not is_opponent_turn, depth + 1))

        return min(scores) if is_opponent_turn else max(scores)

    @staticmethod
    def _winner(state):
        lines = (
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6),
        )
        for first, second, third in lines:
            if state[first] != "." and state[first] == state[second] == state[third]:
                return state[first]
        return None
