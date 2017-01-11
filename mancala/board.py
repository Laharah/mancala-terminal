'simulates a board for mancala'
import itertools
from collections import namedtuple

Score = namedtuple("Score", "top, bottom")


class State:
    '''an extension of a namedtuple like object. Board becomes a mutable wrapper for easy
    interaction and progression. Also allows for easy dependancy injection through
    multiple inheratance'''
    TOP = 1
    BOTTOM = 0

    def __init__(self, seeds=4, *, top=None, bottom=None, turn=0):
        self.top = tuple(top) if top else tuple([seeds] * 6 + [0])
        self.bottom = tuple(bottom) if bottom else tuple([seeds] * 6 + [0])
        self._turn = turn

    @property
    def turn(self):
        return self._turn

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
        return self.top[-1]

    @property
    def bottom_store(self):
        return self.bottom[-1]

    @property
    def score(self):
        return Score(self.top_store, self.bottom_store)

    def next_turn(self):
        return self.BOTTOM if self.turn is self.TOP else self.TOP

    def after_move(self, move):
        'move is the index that player self.turn wants to use. yields the resulting state'
        # constructs a looping iterator for placing seeds
        if self.turn == self.TOP:
            move += 7

        new_vals = list(itertools.chain(self.bottom, self.top))
        i_cycle = itertools.cycle(range(len(new_vals)))
        if self.turn == self.TOP:
            i_cycle = filter(lambda v: v != 7, i_cycle)
        else:
            i_cycle = filter(lambda v: v != 13, i_cycle)

        i_cycle = itertools.dropwhile(lambda i: i <= move, i_cycle)
        seeds = new_vals[move]
        new_vals[move] = 0

        while seeds:
            index = next(i_cycle)
            new_vals[index] += 1
            seeds -= 1

        if index != 6 and index != 13:
            new_turn = self.next_turn()
        else:
            new_turn = self.turn

        if new_vals[index] == 1:
            opposite = self._opposing_house(index)
            if 0 < index < 6 and self.turn == self.BOTTOM:
                new_vals[index] += new_vals[opposite]
                new_vals[opposite] = 0

            elif 7 < index < 13 and self.turn == self.TOP:
                new_vals[index] += new_vals[opposite]
                new_vals[opposite] = 0

        if sum(new_vals[:6] if self.turn == self.BOTTOM else new_vals[7:-1]) == 0:
            # game is over
            new_vals[6] += sum(new_vals[:6])
            new_vals[-1] += sum(new_vals[7:-1])
            new_vals[:6] = new_vals[7:-1] = [0] * 6
            new_turn = None

        return State(bottom=new_vals[:7], top=new_vals[7:], turn=new_turn)

    @staticmethod
    def _opposing_house(index):
        offset = abs(6 - index)
        if index < 6:
            return 6 + offset
        else:
            return 6 - offset


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

    def __call__(self, move):
        self._apply(super().after_move(move))

    def swap_turn(self):
        self.turn = super().next_turn()
