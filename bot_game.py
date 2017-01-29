'pits two basic bots against eachother, used for benchmarking'

import random
from mancala.game import Game
from mancala.player import Bot

random.seed(0)

g = Game(Bot(), Bot())
g()
print(g.score)
