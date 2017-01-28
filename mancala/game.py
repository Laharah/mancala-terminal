from .board import Board
from .errors import IllegalMove


class Game:
    'p1 and p2 are functions that return a move when given a board'

    def __init__(self, player_bottom, player_top):
        self.board = Board()
        self.top = player_top
        self.bottom = player_bottom
        self.player = {
            self.board.TOP: self.top,
            self.board.BOTTOM: self.bottom,
            -1: None
        }
        self.player_number = {self.top: Board.TOP, self.bottom: Board.BOTTOM, -1: None}

    @property
    def turn(self):
        'return the player whos turn it is.'
        return self.player[self.board.turn]

    @turn.setter
    def turn(self, value):
        assert value in (self.top, self.bottom)
        self.board.turn = Board.TOP if value is self.top else Board.BOTTOM

    @property
    def score(self):
        return self.board.score

    @property
    def game_over(self):
        return self.turn is None

    @property
    def winner(self):
        if not self.game_over:
            return None
        score = self.board.score
        return self.top if score.top < score.bottom else self.bottom

    def __call__(self):
        board = self.board
        while board.turn != -1:
            self.execute_turn()

    def execute_turn(self, player=None):
        'executes a single turn, optional player to override player function'
        player = player if player else self.player[self.board.turn]
        valid_move = False
        invalid_move_counter = 0
        while not valid_move:
            safe_board = Board.from_state(self.board.get_state())
            move = player(safe_board)
            try:
                self.board(move)
            except (IndexError, IllegalMove):
                invalid_move_counter += 1
                if invalid_move_counter >= 4:
                    raise
            else:
                valid_move = True
