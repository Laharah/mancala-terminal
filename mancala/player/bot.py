import functools
from ..board import State


class Bot:
    def __init__(self):
        self.side = None
        self.mem_cache = {}
        self.utility = self.memo(self.utility)

    def memo(self, func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                return self.mem_cache[func, args]
            except KeyError:
                result = self.mem_cache[func, args] = func(*args, **kwargs)
                return result

        return inner

    @staticmethod
    def available_moves(state):
        yield from (i for i, v in enumerate(state.current_side[:-1]) if v != 0)

    def estimate_utility(self, state):
        'the estimated utility: store points + 1 for every house that can make it to the store'
        my_side = state.top if self.side == state.TOP else state.bottom
        other_side = state.bottom if my_side is state.top else state.top
        my_store = my_side[-1]
        other_store = other_side[-1]
        my_store += self.canidate_houses(my_side)
        other_store += self.canidate_houses(other_side)
        return (my_store - other_store) / 200

    @staticmethod
    def canidate_houses(side):
        size = len(side)
        canidates = 0
        for i in range(size):
            if side[i] >= size - (i + 1):
                canidates += 1
        return canidates

    def utility(self, state, max_depth=5):
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

        if max_depth <= 0 and state.turn != self.side:
            return self.estimate_utility(state)

        best_move = max(
            self.available_moves(state),
            key=lambda m: self.quality(m, state, max_depth=max_depth - 1))
        return self.utility(state.after_move(best_move), max_depth=max_depth)

    def quality(self, move, state, max_depth=4):
        return self.utility(state.after_move(move), max_depth=max_depth)

    def __call__(self, board):
        if self.side is None: self.side = board.turn
        self.mem_cache = {}
        moves = sorted((self.quality(m, board), m) for m in self.available_moves(board))
        print(moves)
        top_moves = [m for m in moves if board.after_move(m[1]).turn == self.side]
        return top_moves[-1][1] if top_moves else moves[-1][1]
