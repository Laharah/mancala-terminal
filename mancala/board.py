'simulates a board for mancala'
import itertools
from collections import namedtuple

Score = namedtuple("Score", "TOP, BOTTOM")
State = namedtuple("State", "top, bottom, turn")

class Board:
    TOP=0
    BOTTOM=1
    def __init__(self, seeds=4):
        'players will be top and botom'
        self.top = [0]+ [seeds]*6
        self.bottom = [0] + [seeds]*6
        self.turn = self.TOP

    def get_state(self):
        return State(tuple(self.top), tuple(self.bottom), self.turn)

    @classmethod
    def from_state(cls, state):
        board = cls()
        board.top = list(state.top)
        board.bottom = list(state.bottom)
        board.turn = state.turn
        return board

    def swap_turn(self):
        self.turn += 1
        self.turn %= 2

    @property
    def top_store(self):
        return self.top[0]

    @property
    def bottom_store(self):
        return self.bottom[0]


    @property
    def score(self):
        return Score(self.top_store, self.bottom_store)
