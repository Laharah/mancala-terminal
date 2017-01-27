import pytest
import itertools
import struct

from ..board import State


def test_state_init():
    s = State()
    assert s.turn == s.BOTTOM
    for t, x in itertools.zip_longest(s.top, (4, 4, 4, 4, 4, 4, 0)):
        assert t == x
    assert s.top == s.bottom


def test_state_init_w_arguments():
    s = State(top=range(7), turn=State.TOP)
    for t, x in itertools.zip_longest(s.top, range(7)):
        assert t == x
    assert s.turn == s.TOP


def test_fixed_board_length():
    with pytest.raises(struct.error):
        s = State(top=range(5))


def test_hashable():
    s = State()
    d = {}
    d[s] = 0
    assert d[s] == 0
