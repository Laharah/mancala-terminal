import functools
import random

from ..board import State, after_move


class Bot:
    def __init__(self, search_depth=8):
        self.side = None
        self.mem_cache = {}
        self._clear_flag = True
        self.search_depth = search_depth

    @staticmethod
    def available_moves(state):
        # yield from (i for i, v in enumerate(state.current_side[-1:0:-1]) if v != 0)
        side = state.current_side
        yield from (i for i in reversed(range(len(side) - 1)) if side[i] > 0)

    def estimate_utility(self, state):
        'the estimated utility: store points + 1 for every house that can make it to the store'
        my_side = state.top if self.side == state.TOP else state.bottom
        other_side = state.bottom if self.side == state.TOP else state.top
        my_store = my_side[-1]
        other_store = other_side[-1]
        my_store += self.canidate_houses(my_side) / 2
        other_store += self.canidate_houses(other_side) / 2
        return (my_store - other_store) / 200

    @staticmethod
    def canidate_houses(side):
        size = len(side)
        canidates = 0
        for i in range(size):
            if side[i] == size - (i + 1):
                canidates += 1
            elif side[i] > size - (i + 1):
                canidates += .5
        return canidates

    def utility(self, state, max_depth=8, alpha=-10, beta=10):
        if state.turn == -1:
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

        if self.side == state.turn:
            v = -10
            for move in self.available_moves(state):
                v = max(
                    v,
                    self.utility(
                        after_move(state, move), max_depth - 1, alpha=alpha, beta=beta))
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return v
        else:
            v = 10
            for move in self.available_moves(state):
                v = min(
                    v,
                    self.utility(
                        after_move(state, move), max_depth - 1, alpha=alpha, beta=beta))
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return v

    def quality(self, move, state, max_depth=8, alpha=-10, beta=10):
        return self.utility(
            after_move(state, move), max_depth=max_depth, alpha=alpha, beta=beta)

    def __call__(self, board):
        if self.side is None: self.side = board.turn
        if self._clear_flag:
            self.mem_cache = {}
        else:
            self._clear_flag = True
        moves = sorted((self.quality(
            m, board.get_state(), max_depth = self.search_depth), m)
                       for m in self.available_moves(board))
        top_moves = [m for m in moves if m[0] == moves[-1][0]]
        print(moves, end=':')
        extra_moves = [m for m in top_moves if after_move(board, m[1]).turn == self.side]
        if extra_moves:
            move = extra_moves[-1]
            self._clear_flag = False
        else:
            move = random.choice(top_moves)
        print(move[1] + 1)
        return move[1]
