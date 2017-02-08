import pytest

from ..display import show_board
from ..player import bot
from ..board import Board
from ..board import State

Bot = bot.Bot


def test_available_moves():
    bot = Bot()
    board = Board()
    assert list(bot.available_moves(board)) == list(reversed(range(6)))
    board.bottom[:3] = [0, 0, 0]
    assert list(bot.available_moves(board)) == [5, 4, 3]


def test_wants_to_win():
    board = Board()
    board.top = [4, 0, 0, 0, 0, 0, 15]
    board.bottom = [0, 0, 0, 0, 2, 1, 17]
    bot = Bot()
    expected_moves = [5, 4, 5]
    for expected in expected_moves:
        move = bot(board)
        assert move == expected
        board(move)
    assert board.turn is -1
    assert board.score == (20, 19)
    print(bot.mem_cache)


@pytest.mark.skip
def test_limit_break():
    board = Board()
    board.bottom = [6, 4, 2, 3, 1, 1, 0]
    board.top = [0, 0, 0, 0, 1, 1, 15]
    bot = Bot()
    expected_moves = [5, 3, 5, 4, 5, 0, 5, 1, 5, 4, 5, 2, 5, 3, 5, 4, 5]
    for expected in expected_moves:
        show_board(board)
        move = bot(board)
        assert move == expected
        board(move)
    assert board.score == (16, 17)


def test_first_move():
    board = Board()
    bot = Bot()
    assert bot(board) == 2


def test_correct_best_move():
    state = State(
        bottom=b'\x03\x00\x00\x02\x00\x01\x0e',
        top=b'\x04\x01\x00\x04\x00\x00\x13',
        turn=0)
    bot = Bot(14)
    bot.side = 0
    assert bot.mtdf(state, 0, depth=14) == 1
    print(bot.mem_cache[state])
    assert bot(Board.from_state(state)) == 5
