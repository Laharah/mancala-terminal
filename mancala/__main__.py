from . import game
from . import player

g = game.Game(player.Human(), player.Human())
g()
print(g.score)
