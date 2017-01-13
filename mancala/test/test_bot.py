import pytest

from ..player import bot
from ..board import Board

Bot = bot.Bot

def test_available_moves():
    bot = Bot()
    board = Board()
    assert list(bot.available_moves(board)) == list(range(6))
    board.bottom[:3] = [0,0,0]
    assert list(bot.available_moves(board)) == [3, 4, 5]

def test_wants_to_win():
    board = Board()
    board.top = [4, 0,0,0,0,0,15]
    board.bottom = [0,0,0,0,2,1,17]
    bot = Bot()
    expected_moves = [5, 4, 5]
    for expected in expected_moves:
        move = bot(board)
        assert move == expected
        board(move)
    assert board.turn is None
    assert board.score == (19, 20)
    print(bot.mem_cache)

@pytest.mark.skip
def test_limit_break():
    board = Board()
    board.bottom = [6, 4, 2, 3, 1, 1, 0]
    board.top = [0, 0, 0, 0, 0, 1, 15]
    bot = Bot()
    expected_moves = [5, 3, 5, 4, 5, 0, 5, 1, 5, 4, 5, 2, 5, 3, 5, 4, 5]
    for expected in expected_moves:
        move = bot(board)
        assert move == expected
        board(move)
    assert board.score == (16, 17)
