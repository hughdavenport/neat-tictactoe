from __future__ import print_function
import neat
import random
import pickle       # pip install cloudpickle


DEBUG = False

best_net = None
best_fitness = None

NUMBER_OF_GAMES_TO_RUN = 100

def isValidMove(board, index):
    return index >= 0 and index < len(board) and board[index] == 0.5

def isFinished(board):
    return isLine(board, 0, 1, 2) \
        or isLine(board, 3, 4, 5) \
        or isLine(board, 6, 7, 8) \
        or isLine(board, 0, 4, 8) \
        or isLine(board, 2, 4, 6) \
        or isDraw(board)

def isDraw(board):
    return board.count(0.5) == 0
    
def isLine(board, i1, i2, i3):
    if i1 < 0 or i2 < 0 or i3 < 0 or i1 >= len(board) or i2 >= len(board) or i3 >= len(board):
        return False
    if board[i1] == 0.5:
        return False
    return board[i1] == board[i2] and board[i1] == board[i3]

def isLineWithEmptyGap(board, i1, i2, i3, player=True):
    if i1 < 0 or i2 < 0 or i3 < 0 or i1 >= len(board) or i2 >= len(board) or i3 >= len(board):
        return False
    row = [board[i1], board[i2], board[i3]]
    return row.count(0.5) == 1 and row.count(0.0 if player else 1.0) == 2

def isWinner(board, player=True):
    if isLine(board, 0, 1, 2):
        return board[0] == (0.0 if player else 1.0)
    if isLine(board, 3, 4, 5):
        return board[3] == (0.0 if player else 1.0)
    if isLine(board, 6, 7, 8):
        return board[6] == (0.0 if player else 1.0)
    if isLine(board, 0, 4, 8):
        return board[0] == (0.0 if player else 1.0)
    if isLine(board, 2, 4, 6):
        return board[2] == (0.0 if player else 1.0)

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
    if isAlmostWinner(board, player):
        return 0.5 # Give some bonus
    if isDraw(board):
        return 0.0 # Get some points for a draw
    return -board.count(0.5) / 9.0 # Penalise empty spaces left

def printBoard(board):
    for y in range(0, 3):
        print("+-+-+-+")
        for x in range(0, 3):
            index = y * 3 + x
            print("|{}".format(' ' if board[index] == 0.5 else ('X' if board[index] == 0.0 else 'O')), end='')
        print("|")
    print("+-+-+-+")

def eval_genome(genome, config, human=False):
    global best_net, best_fitness
    genome.fitness = 0.0
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    if best_net is None:
        print("Using a random opponent")
        best_net = net
    for g in range(0, NUMBER_OF_GAMES_TO_RUN): # Run a few games
        board = [0.5 for i in range(0, 9)]
        playerFirst = random.random() > 0.5
        steps = []
        opp_steps = []
        while not isFinished(board):
            if playerFirst:
                output = net.activate(board)
                index = sorted(range(len(output)), key=lambda x: output[x])[-1]
                if not isValidMove(board, index):
                    genome.fitness -= 0.5 # Penalty for doing wrong move
                    if DEBUG:
                        print("Bad move from player")
                    break

                board[index] = 0.0
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
                    if g < NUMBER_OF_GAMES_TO_RUN / 2 and False:
                        indices = [i for i, v in enumerate(board) if v == 0.5]
                        index = random.choice(indices)
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

                board[index] = 1.0
                steps.append(index)
                if DEBUG or human:
                    print("Opponent at {}, {}".format(int(index / 3), int(index % 3)))
                    printBoard(board)
            else:
                index = None
                if human:
                    index = int(input("Enter an index: "))
                else:
                    if g < NUMBER_OF_GAMES_TO_RUN / 2 and False:
                        indices = [i for i, v in enumerate(board) if v == 0.5]
                        index = random.choice(indices)
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

                board[index] = 1.0
                steps.append(index)
                if DEBUG or human:
                    print("Opponent at {}, {}".format(int(index / 3), int(index % 3)))
                    printBoard(board)

                if isFinished(board):
                    break

                output = net.activate(board)
                index = sorted(range(len(output)), key=lambda x: output[x])[-1]
                if not isValidMove(board, index):
                    genome.fitness -= 0.5 # Penalty for doing wrong move
                    if DEBUG:
                        print("Bad move from player")
                    break

                board[index] = 0.0
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
    if DEBUG:
        print("Final fitness = {}".format(genome.fitness))
    if best_fitness is None:
        best_fitness = genome.fitness
    if genome.fitness > best_fitness:
        print("Setting new opponent, fitness = {}, it was {}".format(genome.fitness, best_fitness))
        best_net = net
        best_fitness = genome.fitness
    return genome.fitness
        
def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)

# Load configuration.
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-feedforward')

config.fitness_threshold = NUMBER_OF_GAMES_TO_RUN * 0.99

# Create the population, which is the top-level object for a NEAT run.
p = neat.Population(config)

# Add a stdout reporter to show progress in the terminal.
p.add_reporter(neat.StdOutReporter(True))

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

