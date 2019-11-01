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

    @property
    def _naughts(self):
        return self._board[0:9]

    @property
    def _crosses(self):
        return self._board[9:18]

    # Constructors

    def __init__(self):
        self._turn = bool(random.getrandbits(1))
        self._player = _CROSS if self._turn else _NAUGHT
        self._board = [0.0] * 18


    @staticmethod
    def _createFromState(state):
        ret = TicTacToe()
        ret._board = state[0:18]
        ret._turn = True if state[18] == 1.0 else False
        return ret

    # Public methods

    def state(self):
        # TODO If we think of changing this to a CNN, then we should use [self._turn] * 9
        #       - AlphaGo does this
        return self._board + [1.0 if self._turn else 0.0]

    def board(self):
        ret = [None] * 9
        for index in range(0, 9):
            if self._naughts[index] == 1.0:
                ret[index] = _NAUGHT
            elif self._crosses[index] == 1.0:
                ret[index] = _CROSS
        return ret

    def player(self):
        return self._player

    def opponent(self):
        return _NAUGHT if self._player == _CROSS else _CROSS

    def isOurTurn(self):
        return self._turn

    def possibleMoves(self):
        if self.isFinished():
            return []
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
            filtered = self.__applyLineFilter(line)
            if filtered.count(_NAUGHT) == 3:
                return _NAUGHT
            elif filtered.count(_CROSS) == 3:
                return _CROSS
        # No winner, either a draw or not finished
        return None

    def score(self):
        if self.isDraw():
            return 0.0
        winner = self.getWinner()
        if winner is None:
            return 0.0
        return 1.0 if winner == self._player else -1.0

    # Private methods

    def __isValidMove(self, index):
        return index >= 0 and index < 9 and self.__isSpaceFree(index)

    def __isSpaceFree(self, index):
        return self._naughts[index] == 0.0 and self._crosses[index] == 0.0

    def __applyLineFilter(self, line):
        return [cell for index, cell in enumerate(self.board()) if line[index] == 1]

    def _almostWinners(self):
        tempGame = TicTacToe._createFromState(self.state())
        ret = []
        for index in range(0, 9):
            try:
                tempGame.playMove(index)
                winner = tempGame.getWinner()
                tempGame = TicTacToe._createFromState(self.state())
                if winner is not None:
                    ret.append(winner)
                    continue
                tempGame._turn = not tempGame._turn
                tempGame.playMove(index)
                winner = tempGame.getWinner()
                tempGame = TicTacToe._createFromState(self.state())
                # Either other player won, or draw
                ret.append(winner)
            except:
                # Invalid move
                ret.append(None)
        return ret

    def _possibleForks(self):
        winners = self._almostWinners()
        if winners.count(None) != 9:
            # We have a one move win, no point looking for forks
            # Good agents should never get this code path!
            return winners
        tempGame = TicTacToe._createFromState(self.state())
        ret = []
        for index in range(0, 9):
            try:
                player = None
                tempGame.playMove(index)
                winners = tempGame._almostWinners()
                tempGame = TicTacToe._createFromState(self.state())
                if winners.count(None) == 7:
                    # We have two winning paths, this is a fork
                    player = next(player for player in winners if player is not None)
                tempGame._turn = not tempGame._turn
                tempGame.playMove(index)
                winners = tempGame._almostWinners()
                tempGame = TicTacToe._createFromState(self.state())
                if winners.count(None) == 7:
                    # We have two winning paths, this is a fork
                    if player is not None:
                        player = (player, next(player for player in winners if player is not None))
                    else:
                        player = next(player for player in winners if player is not None)
                ret.append(player)
            except:
                ret.append(None)
        return ret

    def __repr__(self):
        return str(self)

    def __str__(self):
        ret = "\n".join([
            "TIC TAC TOE",
            "Our token: {}".format(self._player)
        ])
        if self.isFinished():
            ret += "\nGame Over: {} won".format(self.getWinner())
        else:
            ret += "\nCurrent turn: {}".format(_CROSS if self._turn else _NAUGHT)
        board = self.board()
        for y in range(0, 3):
            if y > 0:
                ret += "\n---+---+---"
            ret +=     "\n   |   |   \n"
            for x in range(0, 3):
                if x > 0:
                    ret += "|"
                char = " " if board[y * 3 + x] is None else board[y * 3 + x]
                ret += " " + char + " "
            ret +=     "\n   |   |   "
        return ret
