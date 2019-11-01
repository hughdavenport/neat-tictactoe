import random

_lines = [
    [1, 1, 1,
     0, 0, 0,
     0, 0, 0],
    [1, 0, 0,
     0, 1, 0,
     0, 0, 1],
    [1, 0, 0,
     1, 0, 0,
     1, 0, 0],
    [0, 1, 0,
     0, 1, 0,
     0, 1, 0],
    [0, 0, 1,
     0, 1, 0,
     1, 0, 0],
    [0, 0, 1,
     0, 0, 1,
     0, 0, 1],
    [0, 0, 0,
     1, 1, 1,
     0, 0, 0],
    [0, 0, 0,
     0, 0, 0,
     1, 1, 1]
]

_NAUGHT = 'O'
_CROSS  = 'X'

class TicTacToe:

    # Private variables

    _board = [0.0] * 18

    @property
    def _naughts(self):
        return self._board[0:9]

    @property
    def _crosses(self):
        return self._board[9:18]

    @property
    def character(self):
        return self._character

    # Constructors

    def __init__(self):
        self._turn = bool(random.getrandbits(1))
        self._character = _CROSS if self._turn else _NAUGHT

    # Public methods

    def isOurTurn(self):
        return self._turn

    def possibleMoves(self):
        return [index for index in range(0, 9) if self._board[index] == 0.0 and self._board[index + 9] == 0.0]

    def playMove(self, index):
        if not self.__isValidMove(index):
            raise IndexError
        if self.isFinished():
            raise Exception("Game finished")
        if self._turn:
            index += 9
        self._board[index] = 1.0
        self._turn = not self._turn

    def isFinished(self):
        return self.getWinner() is not None or self.isDraw()

    def isDraw(self):
        return self._board.count(1.0) == 9

    def getWinner(self):
        for line in _lines:
            lines = self.__applyLineFilter(line)
            if lines[0].count(1.0) == 3:
                return _NAUGHT
            if lines[1].count(1.0) == 3:
                return _CROSS
        # No winner, either a draw or not finished
        return None

    def score(self):
        if self.isDraw():
            return 0.0
        winner = self.getWinner()
        if winner is None:
            return 0.0
        return 1.0 if winner == self._character else -1.0

    # Private methods

    def __isValidMove(self, index):
        return index >= 0 and index < 9 and self.__isSpaceFree(index)

    def __isSpaceFree(self, index):
        return self._naughts[index] == 0.0 and self._crosses[index] == 0.0

    def __applyLineFilter(self, line):
        return [
            [cell for index, cell in enumerate(self._naughts) if line[index] == 1],
            [cell for index, cell in enumerate(self._crosses) if line[index] == 1]
        ]

    def __repr__(self):
        return str(self)

    def __str__(self):
        ret = "\n".join([
            "TIC TAC TOE",
            "Our token: {}".format(self._character)
        ])
        if self.isFinished():
            ret += "\nGame Over: {} won".format(self.getWinner())
        else:
            ret += "\nCurrent turn: {}".format(_CROSS if self._turn else _NAUGHT)
        for y in range(0, 3):
            if y > 0:
                ret += "\n---+---+---"
            ret +=     "\n   |   |   \n"
            for x in range(0, 3):
                if x > 0:
                    ret += "|"
                char = " "
                if self._board[x * 3 + y] == 1.0:
                    char = _NAUGHT
                elif self._board[9 + x * 3 + y] == 1.0:
                    char = _CROSS
                ret += " " + char + " "
            ret +=     "\n   |   |   "
        return ret



    # TODO make subclasses for diff agents
    #       - random
    #       - perfect
    #       - losing

    # TODO also add more private functions
    #       - list of almost wins (kinda needed for losing agent)
