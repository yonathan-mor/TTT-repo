from board import board
from randomplayer import randomplayer

class environment:
    def __init__(self):
        self.board = board()
        self.player1 = randomplayer("O")
        self.agentmark = "X"
        self.WIN_REWARD = 10
        self.LOSS_REWARD = -12
        self.DRAW_REWARD = 5
        self.MOVE_REWARD = 0
        self.ILLEGAL_REWARD = -1
        self.result = None
    def get_state(self):
        # The immutable board string can also be used as a Q-table key.
        return self.board.to_key()
    def reset(self, agent_starts):
        self.board.restart()
        self.result = None
        if not agent_starts:
            self.player1.choose_move(self.board)
        return self.get_state()
    def step(self, action):
        # action is a cell index 0-8 -> (row, col)
        if not isinstance(action, int) or action not in range(9):
            return self.get_state(), self.ILLEGAL_REWARD, False
        pos = divmod(action, 3)
        if not self.board.make_move(pos, self.agentmark):
            return self.get_state(), self.ILLEGAL_REWARD, False
        if self.board.winner() == self.agentmark:
            self.result = "win"
            return self.get_state(), self.WIN_REWARD, True
        if self.board.is_full():
            self.result = "draw"
            return self.get_state(), self.DRAW_REWARD, True
        self.player1.choose_move(self.board)
        if self.board.winner() == self.player1.symbol:
            self.result = "loss"
            return self.get_state(), self.LOSS_REWARD, True
        if self.board.is_full():
            self.result = "draw"
            return self.get_state(), self.DRAW_REWARD, True
        return self.get_state(), self.MOVE_REWARD, False
    def get_result(self):
        return self.result