Mancala-Terminal
=================
## a simple terminal version of mancala built as a coding exercise

*python 3 only*

to play simply download the repo, open it and type:

`python -m mancala`

**requires a terminal that supports unicode output, may not work on windows**

tests can be run with pytest

Currently the game has a crude and poorly optimized bot to play against.

###### TODO:
* improve bot
   * speed/space optimizations, lots of room for improvement here
     - combine bot mem_cache and after_move memoization into single transposition table (with best move?)
     - futility pruning in alpha-beta (not easily implemented with advanced estimation heuristic)
     - enhanced transposition cutoffs (examine child nodes for cutoffs before recursing)
     - endgame databases, too slow to compute at current speeds.
   * 'solve' the game?
   * train a ML replacement for bot if realtime solving infeasible?
   * go nuclear (rewrite bot into c extension)
* implement fallback to ascii for non utf-8 compliant terminals
* refactor rule logic into game module for better separation of concerns
