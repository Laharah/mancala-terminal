#!/usr/bin/env python3
'pits two basic bots against eachother, used for benchmarking'

import random
import sys
from mancala.game import Game
from mancala.player import Bot

random.seed(0)
a = b = 8
try:
    a = int(sys.argv[1])
    b = int(sys.argv[2])
except IndexError:
    pass
g = Game(Bot(a), Bot(b))
g()
print(g.score)
