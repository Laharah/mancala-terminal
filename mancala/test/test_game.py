import pytest
import random
from unittest.mock import Mock

from ..game import Game
from ..board import Board
from ..errors import IllegalMove


@pytest.fixture
def random_player():
    def p(board):
        my_side = board.top if board.turn == board.TOP else board.bottom
        return random.choice([i for i, v in enumerate(my_side[:-1]) if v != 0])

    return p


def test_calls_players():
    p1 = Mock(return_value=2)
    p2 = Mock()
    game = Game(p1, p2)
    game.execute_turn(player=p1)
    assert p1.called


def test_gives_board():
    p1 = Mock(return_value=2)
    p2 = Mock()
    g = Game(p1, p2)
    g.execute_turn()
    assert p1.called
    assert isinstance(p1.call_args[0][0], Board)


def test_gives_to_correct_player():
    p1 = Mock(return_value=2)
    p2 = Mock(return_value=2)
    g = Game(p1, p2)
    assert g.turn is g.bottom  # p1
    g.turn = g.top  #set to p2's turn
    g.execute_turn()
    assert not p1.called
    assert p2.called


def test_anti_cheat():
    def p1(board):
        if board.turn == board.TOP:
            my_side = board.top
        else:
            my_side = board.bottom
        my_side[-1] = 100
        return 2

    p2 = Mock()
    g = Game(p1, p2)
    g.execute_turn()
    assert g.score == (0, 1)


def test_game_loop(random_player):
    p1 = random_player
    p2 = random_player
    g = Game(p1, p2)
    g()
    assert g.turn == None
    assert g.game_over
    print(g.score)


def test_requery_on_invalid():
    p1 = Mock()
    p1.side_effect = [1, 10, 2]
    p2 = Mock()
    g = Game(p1, p2)
    g.board.bottom[1] = 0
    g.execute_turn()
    assert p1.call_count == 3
    assert not p2.called


def test_raise_error_after_4_invalid_moves():
    p1 = Mock()
    p1.side_effect = [1, 22, 1, 1]
    p2 = Mock()
    g = Game(p1, p2)
    g.board.bottom[1] = 0
    with pytest.raises(IllegalMove):
        g()
    assert p1.call_count == 4
