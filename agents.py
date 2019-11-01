from game import TicTacToe
import random

class RandomAgent:

    def activate(self, inputs):
        game = TicTacToe._createFromState(inputs)
        possibles = game.possibleMoves()
        return [random.random() if index in possibles else 0.0 for index in range(0, 9)]

class PerfectAgent:

    def __init__(self, player):
        self._player = player

    def activate(self, inputs):
        # From pseudo code at  https://en.wikipedia.org/wiki/Tic-tac-toe#Strategy
        game = TicTacToe._createFromState(inputs)
        winners = game._almostWinners()

        # 1. Win
        for index in range(0, len(winners)):
            if winners[index] == self._player:
                # We will win
                return [1.0 if i == index else 0.0 for i in range(0, 9)]

        # 2. Block
        for index in range(0, len(winners)):
            if winners[index] is not None:
                # We will stop them winning
                return [1.0 if i == index else 0.0 for i in range(0, 9)]
        # We can assume winners only has None's in it now

        forks = game._possibleForks()

        # 3. Fork
        for index in range(0, len(forks)):
            if forks[index] == self._player or (forks[index] is not None and self._player in forks[index]):
                return [1.0 if i == index else 0.0 for i in range(0, 9)]

        opponentsForks = [True if fork is not None and fork != self._player else False for fork in forks]
        count = opponentsForks.count(True)
        possibles = game.possibleMoves()

        # 4. Block an opponent's fork
        if count > 0:
            if count == 1:
                index = opponentsForks.index(True)
                return [1.0 if i == index else 0.0 for i in range(0, 9)]
            blocksWithNoForks = []
            for index in possibles:
                game.playMove(index)
                try:
                    # This will raise exception if not forcing a block
                    forcedIndex = game._almostWinners().index(self._player)
                    if all([True if fork is None or fork == self._player else False for fork in game._possibleForks()]):
                        # We can force a block and block all forks
                        return [1.0 if i == index else 0.0 for i in range(0, 9)]
                    elif not opponentsForks[forcedIndex]:
                        # We can force a block which doesn't force a fork, use if we can't block all forks
                        blocksWithNoForks.append(index)
                except:
                    # We couldn't force a block
                    pass
                game = TicTacToe._createFromState(inputs)
            if len(blocksWithNoForks) > 0:
                return [1.0 if i == blocksWithNoForks[0] else 0.0 for i in range(0, 9)]

        # 5. Centre
        if 4 in possibles:
            return [1.0 if i == 4 else 0.0 for i in range(0, 9)]

        # 6. Opposite corner
        board = game.board()
        if 0 in possibles and board[8] not in [None, self._player]:
            return [1.0 if i == 0 else 0.0 for i in range(0, 9)]
        if 8 in possibles and board[0] not in [None, self._player]:
            return [1.0 if i == 8 else 0.0 for i in range(0, 9)]
        if 2 in possibles and board[6] not in [None, self._player]:
            return [1.0 if i == 2 else 0.0 for i in range(0, 9)]
        if 6 in possibles and board[2] not in [None, self._player]:
            return [1.0 if i == 6 else 0.0 for i in range(0, 9)]

        # 7. Empty corner
        if 0 in possibles:
            return [1.0 if i == 0 else 0.0 for i in range(0, 9)]
        if 2 in possibles:
            return [1.0 if i == 2 else 0.0 for i in range(0, 9)]
        if 6 in possibles:
            return [1.0 if i == 6 else 0.0 for i in range(0, 9)]
        if 8 in possibles:
            return [1.0 if i == 8 else 0.0 for i in range(0, 9)]

        # 8. Empty side
        if 1 in possibles:
            return [1.0 if i == 1 else 0.0 for i in range(0, 9)]
        if 3 in possibles:
            return [1.0 if i == 3 else 0.0 for i in range(0, 9)]
        if 5 in possibles:
            return [1.0 if i == 5 else 0.0 for i in range(0, 9)]
        if 7 in possibles:
            return [1.0 if i == 7 else 0.0 for i in range(0, 9)]

class LosingAgent:

    def activate(self, inputs):
        game = TicTacToe._createFromState(inputs)
        winners = game._almostWinners()
        possibles = game.possibleMoves()
        moves = [random.random() if index in possibles and winners[index] is None else 0.0 for index in range(0, 9)]
        if moves.count(0.0) == 9:
            return [random.random() if index in possibles else 0.0 for index in range(0, 9)]
        return moves
