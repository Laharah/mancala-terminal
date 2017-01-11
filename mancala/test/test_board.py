import pytest
from ..board import Board


@pytest.fixture
def sample_board():
    b = Board()
    b.top[2] = 0
    for i in range(3, 7):
        b.top[i] += 1
    b.swap_turn()
    return b


def test_create():
    b = Board()
    assert b.top == b.bottom == [0, 4, 4, 4, 4, 4, 4]


def test_swap_turn():
    b = Board()
    t = b.turn
    b.swap_turn()
    assert b.turn != t
    b.swap_turn()
    assert b.turn == t


def test_stores():
    b = Board()
    assert b.top_store == 0
    assert b.bottom_store == 0


def test_score():
    b = Board()
    score = b.score
    assert score == (0, 0)
    assert score.TOP == 0
    assert score.BOTTOM == 0


def test_get_state():
    b = Board()
    initial_side = (0, 4, 4, 4, 4, 4, 4)
    assert b.get_state() == (initial_side, initial_side, b.TOP)


def test_state_hashable(sample_board):
    d = {}
    d[0] = sample_board.get_state()
    assert d[0] == sample_board.get_state()

def test_board_not_hasable(sample_board):
    d = {}
    with pytest.raises(TypeError):
        d[sample_board] = 'error'

def test_from_state(sample_board):
    state = sample_board.get_state()
    b = Board.from_state(state)
    assert b is not sample_board
    assert b.top == sample_board.top
    assert b.bottom == sample_board.bottom
    assert b.turn == sample_board.turn
