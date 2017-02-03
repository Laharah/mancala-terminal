import functools
import random

from ..board import State, after_move


class Bot:
    def __init__(self, search_depth=8):
        self.side = None
        self.mem_cache = {}  #format state:[lower, upper]
        self.search_depth = search_depth

    @staticmethod
    def available_moves(state):
        # yield from (i for i, v in enumerate(state.current_side[-1:0:-1]) if v != 0)
        side = state.current_side
        yield from (i for i in reversed(range(len(side) - 1)) if side[i] > 0)

    def estimate_utility(self, state):
        'the estimated utility: store points + 1 for every house that can make it to the store'
        stores = state.bottom_store, state.top_store
        if self.side == state.BOTTOM:
            return stores[0] - stores[1]
        else:
            return stores[1] - stores[0]

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

    def order_moves(self, pairs, original):
        'given (move,state) pairs order them by most likely to succeed'
        #cached hints
        #extra_turns
        #captures (expensive, turned off for now)
        #left to right
        ordered = []
        for m, state in pairs:
            # capture = 0
            # end = m + original.current_side[m] % 13
            # if end < 6:
            #     if original.opposing_side[5 - m]:
            #         capture = -1

            # we invert for our side so better positions come first, not needed
            # on opposing side)
            turn = original.turn
            sign = -1 if turn == self.side else 1
            index = 1 if turn == self.side else 0

            ordered.append((self.mem_cache.get(state, (0,0))[index] * sign,
                -1 if original.turn == state.turn else 0,
                # capture,
                5 - m,
                m, state))  #these last two do not affect sort, used for id

        ordered.sort()
        return (o[-2:] for o in ordered)

    def utility(self, state, max_depth=8, alpha=-100, beta=100):
        try:
            lower, upper = self.mem_cache[state]
        except KeyError:
            lower, upper = -100, 100
        else:
            if lower >= beta: return lower
            if upper <= alpha: return upper
            alpha = max(alpha, lower)
            beta = min(beta, upper)

        if state.turn == -1:
            return self.estimate_utility(state)


        move_state_pairs = ((m, after_move(state, m))
                            for m in self.available_moves(state))
        moves = self.order_moves(move_state_pairs, state)

        if max_depth <= 0:
            v = self.estimate_utility(state)

        elif self.side == state.turn:
            v = -10
            for move, n_state in moves:
                v = max(v, self.utility(n_state, max_depth - 1, alpha=alpha, beta=beta))
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
        else:
            v = 10
            for move, n_state in moves:
                v = min(v, self.utility(n_state, max_depth - 1, alpha=alpha, beta=beta))
                beta = min(beta, v)
                if beta <= alpha:
                    break

        if v <= alpha:
            upper = v
        if alpha < v < beta:
            lower = upper = v
        if v >= beta:
            lower = v
        self.mem_cache[state] = [lower, upper]
        return v

    def quality(self, move, state, max_depth=8, alpha=-10, beta=10):
        return self.utility(
            after_move(state, move), max_depth=max_depth, alpha=alpha, beta=beta)

    def __call__(self, board):
        if self.side is None: self.side = board.turn
        moves = sorted((self.quality(
            m, board.get_state(), max_depth=self.search_depth), m)
                       for m in self.available_moves(board))
        top_moves = [m for m in moves if m[0] == moves[-1][0]]
        print(moves, end=':')
        extra_moves = [m for m in top_moves if after_move(board, m[1]).turn == self.side]
        if extra_moves:
            move = extra_moves[-1]
        else:
            move = random.choice(top_moves)
        print(move[1] + 1)
        return move[1]
