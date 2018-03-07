'simulates a board for mancala'
import itertools
import struct
from collections import namedtuple
from .errors import IllegalMove
from .utils import memo
import cstate

Score = namedtuple("Score", "bottom, top")
BINCODE = struct.Struct('BBBBBBBBBBBBBBb')


class State:
    '''an extension of a namedtuple like object. Board becomes a mutable wrapper for easy
    interaction and progression. Also allows for easy dependancy injection through
    multiple inheratance'''
    __slots__ = '_bstring'
    TOP = 1
    BOTTOM = 0

    def __init__(self, seeds=4, *, top=None, bottom=None, turn=0, _bstring=None):
        if _bstring:
            self._bstring = _bstring
            return
        top = top if top else [seeds] * 6 + [0]
        bottom = bottom if bottom else [seeds] * 6 + [0]
        self._bstring = BINCODE.pack(*itertools.chain(bottom, top), turn)

    @property
    def top(self):
        return self._bstring[7:-1]

    @property
    def bottom(self):
        return self._bstring[:7]

    @property
    def turn(self):
        t = self._bstring[-1]
        if t == 255:
            return -1
        else:
            return t

    @property
    def current_side(self):
        return self.bottom if self.turn == self.BOTTOM else self.top

    @property
    def opposing_side(self):
        return self.bottom if self.turn == self.TOP else self.top

    def __getitem__(self, index):
        return (self.top, self.bottom, self.turn)[index]

    def __repr__(self):
        return '{}(bottom={}, top={}, turn={})'.format(self.__class__.__name__,
                                                       self.bottom, self.top, self.turn)

    def __eq__(self, other):
        if not isinstance(other, State):
            other = State.from_tuple(other)
        c1 = self.top, self.bottom
        c2 = other.top, other.bottom
        if self.turn == other.turn:
            for s, o in zip(c1, c2):
                if all(a == b for a, b in itertools.zip_longest(s, o)):
                    return True
        return False

    @classmethod
    def duplicate(cls, state_like):
        'create new state from an existing state-like object'
        s = state_like
        n = cls(top=s.top, bottom=s.bottom, turn=s.turn)
        return n

    @classmethod
    def from_tuple(cls, state):
        s = cls(top=state[0], bottom=state[1], turn=state[2])
        return s

    def __hash__(self):
        return hash(self._bstring)

    @property
    def top_store(self):
        return self.top[-1]

    @property
    def bottom_store(self):
        return self.bottom[-1]

    @property
    def score(self):
        return Score(self.bottom_store, self.top_store)

    def next_turn(self):
        return self.BOTTOM if self.turn == self.TOP else self.TOP

    @staticmethod
    def _opposing_house(index):
        offset = abs(6 - index)
        if index < 6:
            return 6 + offset
        else:
            return 6 - offset


@memo
def after_move(state, move):
    try:
        return State(_bstring=cstate.after_move(state._bstring, move))
    except ValueError:
        raise IllegalMove("Must choose a house with seeds.") from None


class Board(State):
    'a mutable wrapper over State'

    def __init__(self, seeds=4, *, top=None, bottom=None, turn=0):
        self._top = list(top) if top else [seeds] * 6 + [0]
        self._bottom = list(bottom) if bottom else [seeds] * 6 + [0]
        assert len(self._top) == len(
            self._bottom) == 7, 'top and bottom must be of length 7'
        self._turn = turn

    @property
    def turn(self):
        return self._turn

    @turn.setter
    def turn(self, n):
        self._turn = n

    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, new):
        self._top = new

    @property
    def bottom(self):
        return self._bottom

    @bottom.setter
    def bottom(self, new):
        self._bottom = new

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

    def __call__(self, move):
        self._apply(after_move(self.get_state(), move))

    def swap_turn(self):
        self.turn = super().next_turn()
