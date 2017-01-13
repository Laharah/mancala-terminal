import functools
from ..board import State

class Bot:

    def __init__(self):
        self.side = None
        self.mem_cache = {}
        self.utility = self.memo(self.utility)
 

    def memo(self, func):
        @functools.wraps(func)
        def inner(*args):
            try:
                return self.mem_cache[func, args]
            except KeyError:
                result = self.mem_cache[func, args] = func(*args)
                return result
        return inner

    @staticmethod
    def available_moves(state):
        yield from (i for i, v in enumerate(state.current_side[:-1]) if v != 0)

    
    def utility(self, state):
        if state.turn is None:
            score = state.score
            if score.top > score.bottom:
                winner = state.TOP
            elif score.bottom > score.top:
                winner = state.BOTTOM
            else:
                winner = None
            if winner is None:
                return 0
            if winner == self.side:
                return 1
            else:
                return -1

        return self.utility(state.after_move(max(self.available_moves(state), key=lambda m: self.quality(m, state))))


    def quality(self, move, state):
        return self.utility(state.after_move(move))


    def __call__(self, board):
        if self.side is None: self.side = board.turn
        moves = sorted((self.quality(m, board), m) for m in self.available_moves(board))
        print(moves)
        return moves[-1][1]
