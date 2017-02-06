from . import game
from . import player
import random

random.seed(0)

g = game.Game(player.Bot(), player.Human())
g()
print(g.score)
