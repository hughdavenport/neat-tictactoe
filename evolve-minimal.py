from __future__ import print_function
import neat
import random
import pickle       # pip install cloudpickle


DEBUG = False

best_net = None
best_fitness = None
last_improved = -1

EVALS_BEFORE_RANDOM = 1000
EVALS_FOR_RANDOM = 1000
NUMBER_OF_GAMES_TO_RUN = 50

def isValidMove(board, index):
    offset = int(len(board) / 2)
    return index >= 0 and index < offset and board[index] == 0 and board[index + offset] == 0

def isFinished(board):
    return isLine(board, 0, 1, 2) \
        or isLine(board, 3, 4, 5) \
        or isLine(board, 6, 7, 8) \
        or isLine(board, 0, 4, 8) \
        or isLine(board, 2, 4, 6) \
        or isDraw(board)

def isDraw(board):
    return board.count(1.0) == 9
    
def isLine(board, i1, i2, i3):
    offset = int(len(board) / 2)
    if i1 < 0 or i2 < 0 or i3 < 0 or i1 >= offset or i2 >= offset or i3 >= offset:
        return False
    if board[i1] == 0 or board[i1 + offset] == 0:
        return False
    return (board[i1] == board[i2] and board[i1] == board[i3]) or \
            (board[i1 + offset] == board[i2 + offset] and board[i1 + offset] == board[i3 + offset])

def isLineWithEmptyGap(board, i1, i2, i3, player=True):
    offset = int(len(board) / 2)
    if i1 < 0 or i2 < 0 or i3 < 0 or i1 >= offset or i2 >= offset or i3 >= offset:
        return False
    if not player:
        i1 += offset
        i2 += offset
        i3 += offset
    row = [board[i1], board[i2], board[i3]]
    return row.count(0.0) == 1 and row.count(1.0) == 2

def isWinner(board, player=True):
    if isLine(board, 0, 1, 2):
        return board[0 if player else 9] == 1.0
    if isLine(board, 3, 4, 5):
        return board[3 if player else 12] == 1.0
    if isLine(board, 6, 7, 8):
        return board[6 if player else 15] == 1.0
    if isLine(board, 0, 4, 8):
        return board[0 if player else 9] == 1.0
    if isLine(board, 2, 4, 6):
        return board[2 if player else 11] == 1.0

def isAlmostWinner(board, player=True):
    return isLineWithEmptyGap(board, 0, 1, 2, player) \
    or isLineWithEmptyGap(board, 3, 4, 5, player) \
    or isLineWithEmptyGap(board, 6, 7, 8, player) \
    or isLineWithEmptyGap(board, 0, 4, 8, player) \
    or isLineWithEmptyGap(board, 2, 4, 6, player)
    
def score(board, player=True):
    if isWinner(board, player):
        return 1.0
    elif isWinner(board, not player):
        return -1.0
    if False:
        if isAlmostWinner(board, player):
            return 0.5 # Give some bonus
        if isDraw(board):
            return 0.0 # Get some points for a draw
        return -board.count(0.5) / 9.0 # Penalise empty spaces left
    return 0.0

def printBoard(board):
    offset = 9
    for y in range(0, 3):
        print("+-+-+-+")
        for x in range(0, 3):
            index = y * 3 + x
            print("|{}".format(' ' if board[index] == 0.0 and board[index + offset] == 0.0 else ('X' if board[index] == 1.0 else 'O')), end='')
        print("|")
    print("+-+-+-+")

import random
class RandomAgent:
    def activate(self, board):
        offset = int(len(board) / 2)
        choices = [index for index in range(0, offset) if board[index] == 0.0 and board[index + offset] == 0.0]
        output = [random.random() if index in choices else 0.0 for index in range(0, offset)]
        return output

def eval_genome(genome, config, human=False):
    global best_net, best_fitness, last_improved
    last_improved += 1
    genome.fitness = 0.0
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    if best_net is None or last_improved > EVALS_BEFORE_RANDOM:
        if best_net is not None:
            print("Haven't improved after a while, resetting to a random opponent, best so far", best_fitness)
        else:
            print("Using a random opponent")
        best_net = RandomAgent()
        last_improved = -EVALS_FOR_RANDOM
    for g in range(0, NUMBER_OF_GAMES_TO_RUN): # Run a few games
        # two 3x3 boards, first is 1 if X has gone, second is if O has gone
        offset = 9
        board = [0 for i in range(0, offset)] * 2
        playerFirst = random.random() > 0.5
        steps = []
        opp_steps = []
        while not isFinished(board):
            if playerFirst:
                output = net.activate(board)
                index = sorted(range(len(output)), key=lambda x: output[x])[-1]
                if not isValidMove(board, index):
                    genome.fitness -= 10.0 / (1 + board.count(1.0)) # Penalty for doing wrong move, less later in the game
                    if DEBUG:
                        print("Bad move from player")
                    break

                board[index] = 1.0
                steps.append(index)
                if DEBUG or human:
                    print("Player at {}, {}".format(int(index / 3), int(index % 3)))
                    printBoard(board)

                if isFinished(board):
                    break

                index = None
                if human:
                    index = int(input("Enter an index: "))
                else:
                    for i in range(0, 10): # Let opponent do bad move a few times if need be
                        output = best_net.activate(board)
                        index = sorted(range(len(output)), key=lambda x: output[x])[-1]
                        if not isValidMove(board, index):
                            index = None
                            # No penalty for opponent doing the same...
                            if DEBUG:
                                print("Bad move from opponent")
                            continue

                if index is None:
                    if DEBUG:
                        print("Several bad moves from opponent")
                    break

                board[index + offset] = 1.0
                steps.append(index)
                if DEBUG or human:
                    print("Opponent at {}, {}".format(int(index / 3), int(index % 3)))
                    printBoard(board)
            else:
                index = None
                if human:
                    index = int(input("Enter an index: "))
                else:
                    for i in range(0, 10): # Let opponent do bad move a few times if need be
                        output = best_net.activate(board)
                        index = sorted(range(len(output)), key=lambda x: output[x])[-1]
                        if not isValidMove(board, index):
                            index = None
                            # No penalty for opponent doing the same...
                            if DEBUG:
                                print("Bad move from opponent")
                            continue

                if index is None:
                    if DEBUG:
                        print("Several bad moves from opponent")
                    break

                board[index + offset] = 1.0
                steps.append(index)
                if DEBUG or human:
                    print("Opponent at {}, {}".format(int(index / 3), int(index % 3)))
                    printBoard(board)

                if isFinished(board):
                    break

                output = net.activate(board)
                index = sorted(range(len(output)), key=lambda x: output[x])[-1]
                if not isValidMove(board, index):
                    genome.fitness -= 10.0 / (1 + board.count(1.0)) # Penalty for doing wrong move, less later in the game
                    if DEBUG:
                        print("Bad move from player")
                    break

                board[index] = 1.0
                steps.append(index)
                if DEBUG or human:
                    print("Player at {}, {}".format(int(index / 3), int(index % 3)))
                    printBoard(board)
        if DEBUG or human:
            if isWinner(board, True):
                print("We won")
                printBoard(board)
            elif isWinner(board, False):
                print("We lost")
                printBoard(board)
            elif isDraw(board):
                print("We drawed")
                printBoard(board)
            else:
                print("Someone played invalid move")
        genome.fitness += score(board, True)
#        if not DEBUG and isAlmostWinner(board, True):
#            print("Almost won, printing steps")
#            board = [0.5 for i in range(0, 9)]
#            player = playerFirst
#            for step in steps:
#                board[step] = 0.0 if player else 1.0
#                player = not player
#                printBoard(board)
#        if not DEBUG and isWinner(board, True):
#            print("We won, will print steps")
#            board = [0.5 for i in range(0, 9)]
#            player = playerFirst
#            for step in steps:
#                board[step] = 0.0 if player else 1.0
#                player = not player
#                printBoard(board)
#        elif not DEBUG and score(board, True) > 0.5: # Have made four moves
#            print("Made more than 4 moves, will print steps")
#            board = [0.5 for i in range(0, 9)]
#            player = playerFirst
#            for step in steps:
#                board[step] = 0.0 if player else 1.0
#                print("{} took move {}, {}".format("Player" if player else "Opponent", int(step / 3), int(step % 3)))
#                printBoard(board)
#                player = not player
    genome.fitness = genome.fitness / NUMBER_OF_GAMES_TO_RUN
    if DEBUG:
        print("Final fitness = {}".format(genome.fitness))
    if best_fitness is None:
        best_fitness = genome.fitness
    if last_improved >= 0 and genome.fitness > best_fitness and genome.fitness >= -1:
        print("Setting new opponent, fitness = {}, it was {}".format(genome.fitness, best_fitness))
        best_net = net
        best_fitness = genome.fitness
        last_improved = -1

    return genome.fitness
        
def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)

# Load configuration.
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-feedforward')

config.fitness_threshold = NUMBER_OF_GAMES_TO_RUN * 0.99
config.fitness_threshold = 0.99999

# Create the population, which is the top-level object for a NEAT run.
p = neat.Population(config)
import sys
if len(sys.argv) >= 2:
    p = neat.Checkpointer.restore_checkpoint(sys.argv[1])

# Add a stdout reporter to show progress in the terminal.
#p.add_reporter(neat.StdOutReporter(True))
p.add_reporter(neat.StdOutReporter(False))

checkpoint = neat.Checkpointer()
p.add_reporter(checkpoint)

stats = neat.StatisticsReporter()
p.add_reporter(stats)

# Run until a solution is found.
winner = None
if True:
    if DEBUG:
        pe = neat.ParallelEvaluator(1, eval_genome)
    else:
        pe = neat.ParallelEvaluator(4, eval_genome)
    winner = p.run(pe.evaluate)
else:
    winner = p.run(eval_genomes)

import visualize
visualize.plot_stats(stats, ylog=False, view=True)
visualize.plot_species(stats, view=True)

# Display the winning genome.
print('\nBest genome:\n{!s}'.format(winner))

# Show output of the most fit genome against training data.
print('\nOutput:')
print(eval_genome(winner, config, True))

with open('winner.pkl', 'wb') as output:
    pickle.dump(winner, output, 1)

