import pytest
from ..board import Board

from .. import errors


@pytest.fixture
def sample_board():
    b = Board()
    b.bottom[1] = 0
    for i in range(2, 6):
        b.bottom[i] += 1
    b.swap_turn()
    return b


def test_create():
    b = Board()
    assert b.top == b.bottom == [4, 4, 4, 4, 4, 4, 0]


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
    assert score.top == 0
    assert score.bottom == 0


def test_get_state():
    b = Board()
    initial_side = (4, 4, 4, 4, 4, 4, 0)
    assert b.get_state() == (initial_side, initial_side, b.BOTTOM)


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


def test_call(sample_board):
    b1 = Board()
    b1(1)
    print(b1)
    print(sample_board)
    assert b1 == sample_board
    b1(2)
    assert b1.score.top == 1
    assert b1.turn == b1.TOP
    b1(3)
    assert b1.score.top == 2
    assert b1.turn == b1.BOTTOM
    assert b1.score.bottom == 0
    assert b1.bottom[:2] == [5, 1]
    assert b1.top == [4, 4, 0, 0, 6, 6, 2]


def test_current_side():
    b = Board()
    assert b.current_side is b.bottom
    b(2)
    assert b.current_side is b.bottom
    b(1)
    assert b.current_side is b.top

def test_opposing_side():
    b = Board()
    assert b.opposing_side is b.top
    b(2)
    assert b.opposing_side is b.top
    b(1)
    assert b.opposing_side is b.bottom


def test_call_steal():
    b1 = Board()
    b1.bottom[0] = 0
    b1.bottom[5] = 8
    assert b1.turn == b1.BOTTOM
    assert b1.top[5] == 4
    b1(5)
    assert b1.bottom[5] == 0
    assert b1.bottom[0] == 6
    assert b1.top[5] == 0


def test_move_on_empty_house():
    b = Board()
    b.bottom[2] == 0
    state = b.get_state()
    assert b.turn == b.BOTTOM
    b(2)
    assert b.get_state() == state


def test_skip_opponent_store():
    b = Board()
    b.top[5] = 10
    bottom_store = b.bottom_store
    b.turn = b.TOP
    b(5)
    assert b.bottom_store == bottom_store
    b.bottom[5] = 10
    top_store = b.top_store
    assert b.turn == b.BOTTOM
    b(5)
    assert b.top_store == top_store


def test_end_on_steal():
    b = Board()
    b.top = [0] * 7
    b.bottom = [0] * 7
    b.top[0] = 1
    b.bottom[4] = 1
    b(4)
    assert sum(b.top) == 0
    assert sum(b.bottom) == 2
    assert b.turn == -1
    assert b.bottom_store == 2


def test_out_of_bounds_move():
    board = Board()
    for move in (6, 10, -2):
        with pytest.raises(IndexError):
            board(move)


def test_house_must_have_seeds():
    b = Board()
    b.bottom[2] = 0
    assert b.turn == b.BOTTOM
    with pytest.raises(errors.IllegalMove) as e:
        b(2)
    assert isinstance(e.value, errors.MancalaError)


def test_game_over():
    b = Board()
    b.bottom = [0] * 5 + [1] + [18]
    assert b.turn == b.BOTTOM
    print(b)
    b(5)
    assert b.turn == -1
    assert b.score.top == 4 * 6
    assert b.score.bottom == 19
