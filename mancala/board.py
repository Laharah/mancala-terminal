'simulates a board for mancala'
import itertools
import struct
from collections import namedtuple
from .errors import IllegalMove
from .utils import memo

Score = namedtuple("Score", "top, bottom")


class State:
    '''an extension of a namedtuple like object. Board becomes a mutable wrapper for easy
    interaction and progression. Also allows for easy dependancy injection through
    multiple inheratance'''
    __slots__ = '_bstring'
    TOP = 1
    BOTTOM = 0
    fmt = 'BBBBBBBBBBBBBBb'

    def __init__(self, seeds=4, *, top=None, bottom=None, turn=0):
        top = top if top else [seeds] * 6 + [0]
        bottom = bottom if bottom else [seeds] * 6 + [0]
        self._bstring = struct.pack(self.fmt, *itertools.chain(bottom, top), turn)

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
        return Score(self.top_store, self.bottom_store)

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
    'move is the index that player state.turn wants to use. yields the resulting state'
    # constructs a looping iterator for placing seeds
    if not 0 <= move < 6:
        raise IndexError('houses 0 through 5 only')
    if state.turn == state.TOP:
        move += 7

    new_vals = list(itertools.chain(state.bottom, state.top))
    i_cycle = itertools.cycle(range(len(new_vals)))
    if state.turn == state.TOP:
        i_cycle = filter(lambda v: v != 6, i_cycle)
    else:
        i_cycle = filter(lambda v: v != 13, i_cycle)

    i_cycle = itertools.dropwhile(lambda i: i <= move, i_cycle)
    seeds = new_vals[move]
    if not seeds:
        raise IllegalMove('you must choose a house with seeds!')
    new_vals[move] = 0
    index = move

    while seeds:
        index = next(i_cycle)
        new_vals[index] += 1
        seeds -= 1

    if index != 6 and index != 13:
        new_turn = state.next_turn()
    else:
        new_turn = state.turn

    if new_vals[index] == 1:
        opposite = state._opposing_house(index)
        if 0 < index < 6 and state.turn == state.BOTTOM:
            new_vals[index] += new_vals[opposite]
            new_vals[opposite] = 0

        elif 7 < index < 13 and state.turn == state.TOP:
            new_vals[index] += new_vals[opposite]
            new_vals[opposite] = 0

    if sum(new_vals[:6]) == 0 or sum(new_vals[7:-1]) == 0:
        # game is over
        new_vals[6] += sum(new_vals[:6])
        new_vals[-1] += sum(new_vals[7:-1])
        new_vals[:6] = new_vals[7:-1] = [0] * 6
        new_turn = -1

    return state.__class__(bottom=new_vals[:7], top=new_vals[7:], turn=new_turn)


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
        self._apply(after_move(self, move))

    def swap_turn(self):
        self.turn = super().next_turn()
