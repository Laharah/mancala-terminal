import functools
import random
import itertools
from pprint import pprint

from ..board import State, after_move


class Bot:
    def __init__(self, search_depth=8):
        self.side = None
        self.mem_cache = {}  #format state:[lower, upper, depth, search_depth]
        self.search_depth = search_depth

    @staticmethod
    def available_moves(state):
        # yield from (i for i, v in enumerate(state.current_side[-1:0:-1]) if v != 0)
        side = state.current_side
        yield from (i for i in reversed(range(len(side) - 1)) if side[i] > 0)

    def estimate_basic(self, state):
        'basic utility, measured by difference between houses'
        stores = state.bottom_store, state.top_store
        if self.side == state.BOTTOM:
            return stores[0] - stores[1]
        else:
            return stores[1] - stores[0]

    def estimate_advanced(self, state):
        'the estimated utility: store points + 1 for every house that can make it to the store'
        my_side = state.top if self.side == state.TOP else state.bottom
        other_side = state.bottom if self.side == state.TOP else state.top
        if state.turn == -1:
            if my_side[-1] > other_side[-1]:
                return 1
            elif my_side[-1] < other_side[-1]:
                return -1
            else:
                return 0
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

            ordered.append((
                self.mem_cache.get(state, (0, 0))[index] * sign,
                -1 if original.turn == state.turn else 0,
                # capture,
                5 - m,
                m,
                state))  #these last two do not affect sort, used for id

        ordered.sort()
        return (o[-2:] for o in ordered)

    def utility(self, state, remaining_depth=8, alpha=-100, beta=100):
        try:
            lower, upper, entry_depth = self.mem_cache[state]
        except KeyError:
            lower, upper = -100, 100
        else:
            if entry_depth >= remaining_depth:
                if lower >= beta: return lower
                if upper <= alpha: return upper
                alpha = max(alpha, lower)
                beta = min(beta, upper)
            else:
                lower, upper, = -100, 100

        if state.turn == -1 or remaining_depth <= 0:
            return self.estimate_advanced(state)

        move_state_pairs = ((m, after_move(state, m))
                            for m in self.available_moves(state))
        moves = self.order_moves(move_state_pairs, state)

        if self.side == state.turn:
            v = -100
            a = alpha
            for move, n_state in moves:
                v = max(
                    v,
                    self.utility(
                        n_state, remaining_depth - 1, alpha=a, beta=beta))
                a = max(alpha, v)
                if v >= beta:
                    break
        else:
            v = 100
            b = beta
            for move, n_state in moves:
                v = min(v,
                        self.utility(
                            n_state,
                            remaining_depth - 1,
                            alpha=alpha,
                            beta=b))
                b = min(b, v)
                if v <= alpha:
                    break

        if v <= alpha:
            # print('fail low')
            upper = v
        if alpha < v < beta:
            lower = upper = v
            print('should not be here!')
        if v >= beta:
            # print('fail high')
            lower = v
        self.mem_cache[state] = [lower, upper, remaining_depth]
        return v

    def iterative_deepening(self, state, max_depth):
        f = -1
        for d in range(1, max_depth, 3):
            f = self.mtdf(state, f, depth=d)
            # print('deepening search')
        f = self.mtdf(state, f, depth=max_depth)
        return f

    def mtdf(self, state, guess, depth=8):
        g = guess
        # print('guess, depth: ', g, depth)
        upperbound = 1000
        lowerbound = -1000
        while lowerbound < upperbound:
            beta = g + .000001 if g == lowerbound else g
            g = self.utility(
                state,
                alpha=beta - .000001,
                beta=beta,
                remaining_depth=depth)
            if g < beta:
                upperbound = g
            else:
                lowerbound = g
            # print(lowerbound, upperbound, g)
            # print('returning: ', g)
            # print('--')
        return g

    def quality(self, move, state, max_depth=8):
        return self.iterative_deepening(after_move(state, move), max_depth)

    def __call__(self, board):
        if self.side is None: self.side = board.turn

        moves = sorted((self.quality(
            m, board.get_state(), max_depth=self.search_depth), m)
                       for m in self.available_moves(board))
        # print(moves)
        # print(self.mem_cache.values())
        # return moves[-1][1]
        top_moves = [m for m in moves if m[0] == moves[-1][0]]
        print(moves, end=':')
        extra_moves = [m for m in top_moves if after_move(board, m[1]).turn == self.side]
        if extra_moves:
            move = extra_moves[-1]
        else:
            move = random.choice(top_moves)
        print(move[1] + 1)
        return move[1]
