import pytest
from contextlib import contextmanager
import io
import sys
from unittest import mock


from ..player import human

from ..board import Board

Human = human.Human

@pytest.fixture
def io_input():
    @contextmanager
    def io_context(buffer):
        sin = sys.stdin
        sys.stdin = buffer
        try:
            yield buffer
        finally:
            sys.stdin = sin
    return io_context

def test_init():
    h = Human()

def test_get_side_from_board(monkeypatch):
    monkeypatch.setitem(__builtins__, 'input', lambda x: '2')
    b = Board()
    h = Human()
    h(b)
    assert h.side == b.BOTTOM

def test_returns_adjusted_input(monkeypatch):
    monkeypatch.setitem(__builtins__, 'input', lambda x: '2')
    b = Board()
    h = Human()
    assert h(b) == 1
