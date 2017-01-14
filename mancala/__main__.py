from . import game
from . import player

g = game.Game(player.Human(), player.Bot())
g()
print(g.score)
