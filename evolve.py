from __future__ import print_function
import neat
import pickle       # pip install cloudpickle
import os

from game import TicTacToe
import agents

NUMBER_TO_SAMPLE = 1000

debug = False

def pickMove(agent, state):
    output = agent.activate(state)
    return sorted(range(len(output)), key=lambda x: output[x])[-1]

def pickAndMakeMove(game, agent):
    state = game.state()
    index = pickMove(agent, state)
    game.playMove(index)

def simulateGame(player, opponent):
    # Returns fitness delta
    game = TicTacToe()
    while not game.isFinished():

        # TODO track stats?

        if game.isOurTurn():
            try:
                pickAndMakeMove(game, player)
            except IndexError:
                # Penalise player
                return -NUMBER_TO_SAMPLE

            if game.isFinished():
                break

            try:
                pickAndMakeMove(game, opponent)
            except IndexError:
                pickAndMakeMove(game, agents.RandomAgent())
        else: # Not our turn
            try:
                pickAndMakeMove(game, opponent)
            except IndexError:
                pickAndMakeMove(game, agents.RandomAgent())

            if game.isFinished():
                break

            try:
                pickAndMakeMove(game, player)
            except IndexError:
                # Penalise player
                return -NUMBER_TO_SAMPLE

    # Game is finished (or illegal move made)

    # TODO debug prints, or stats

    return game.score()

def eval_genome(genome, config):
    genome.fitness = 0.0
    player = neat.nn.FeedForwardNetwork.create(genome, config)
    opponent = agents.RandomAgent()

    for _ in range(0, NUMBER_TO_SAMPLE):
        genome.fitness += simulateGame(player, opponent)
    genome.fitness /= NUMBER_TO_SAMPLE

    # TODO also want to track who is our opponent
    #      or do we want to have that done in bunches
    #      i.e. we should pick best/worst/random ai to be opponent?
    #      or multiple?

    # I would be keen to pick the best/worst after every X generation(s)
    # would probably need to do this in the neat framework

    # TODO think about fitness RE perfect players playing each others

    return genome.fitness

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)

def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # TODO restart from checkpoint

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(100))

    # TODO parallelise 

    # Run for up to 300 generations.
    winner = None
    if debug:
        winner = p.run(eval_genomes, 300)
    else:
        pe = neat.ParallelEvaluator(4, eval_genome)
        winner = p.run(pe.evaluate)

    # TODO visulize, save

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.

    # TODO parse sysargs

    # TODO have human/replay mode

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)
