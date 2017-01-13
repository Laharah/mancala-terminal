from mancala.display import show_board


class Human:
    def __init__(self):
        self.side = None

    def __call__(self, board):
        if self.side is None: self.side = board.turn
        show_board(board)
        i = input('\nYou are {}. What is your move?: '.format(self.side_name))
        return int(i) - 1

    @property
    def side_name(self):
        return 'Bottom' if self.side == 0 else 'Top'
