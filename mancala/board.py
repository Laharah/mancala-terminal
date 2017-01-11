'simulates a board for mancala'
import itertools
from collections import namedtuple

Score = namedtuple("Score", "TOP, BOTTOM")
State = namedtuple("State", "top, bottom, turn")

class State:
    '''an extension of a namedtuple like object. Board becomes a mutable wrapper for easy
    interaction and progression. Also allows for easy dependancy injection through
    multiple inheratance'''
    TOP = 0
    BOTTOM = 1

    def __init__(self, seeds=4, *, top=None, bottom=None, turn=None):
        self.top = tuple(top) if top else tuple([0] + [seeds] * 6)
        self.bottom = tuple(bottom) if bottom else tuple([0] + [seeds] * 6)
        self._turn = turn if turn else self.TOP

    @property
    def turn(self):
        return self._turn

    def __getitem__(self, index):
        return (self.top, self.bottom, self.turn)[index]


    def __eq__(self, other):
        if not isinstance(other, State):
            other = State.from_tuple(other)
        cmps = {self.top:other.top,
                self.bottom: other.bottom}
        if self.turn == other.turn:
            for s, o in cmps.items():
                if all(a == b for a,b in itertools.zip_longest(s, o)):
                    return True
        return False

    @classmethod
    def duplicate(cls, state_like):
        'create new state from an existing state-like object'
        s = cls()
        s.top = tuple(state_like.top)
        s.bottom = tuple(state_like.bottom)
        s._turn = state_like.turn
        return s

    @classmethod
    def from_tuple(cls, state):
        s = cls()
        s.top = tuple(state[0])
        s.bottom = tuple(state[1])
        s._turn = state[2]
        return s

    def __hash__(self):
        return hash((self.top, self.bottom, self._turn))

    @property
    def top_store(self):
        return self.top[0]

    @property
    def bottom_store(self):
        return self.bottom[0]

    @property
    def score(self):
        return Score(self.top_store, self.bottom_store)


    def next_turn(self):
        return self.BOTTOM if self.turn is self.TOP else self.TOP


class Board(State):
    'a mutable wrapper over State'

    def __init__(self, seeds=4):
        super().__init__(seeds=seeds)
        self.top = list(self.top)
        self.bottom = list(self.bottom)

    @property
    def turn(self):
        return self._turn
    
    @turn.setter
    def turn(self, n):
        self._turn = n

    def __hash__(self):
        raise TypeError('Unhashable type: \'Board\'')


    def get_state(self):
        'returns a serialized and hashable version of this boards state'
        return State.duplicate(self)

    @classmethod
    def from_state(cls, state):
        board = cls()
        board._apply(state)
        return board

    def _apply(self, state):
        'apply a given state to current board'
        self.top = list(state.top)
        self.bottom = list(state.bottom)
        self.turn = state.turn


    def swap_turn(self):
        self.turn = super().next_turn()

