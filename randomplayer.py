import random


class randomplayer:
    def __init__(self, symbol):
        self.symbol = symbol

    def choose_move(self, game_board):
        moves = game_board.available_moves()
        if not moves:
            return None

        move = random.choice(moves)
        game_board.make_move(move, self.symbol)
        return move
