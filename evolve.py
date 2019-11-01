from __future__ import print_function
import neat
import pickle       # pip install cloudpickle

from game import TicTacToe
import agents

def pickMove(agent, state):
    output = agent.activate(state)
    return sorted(range(len(output)), key=lambda x: output[x])[-1]

def pickAndMakeMove(game, agent):
    state = game.state()
    game.playMove(pickMove(opponent, state))

def simulateGame(player, opponent):
    # Returns fitness delta
    game = TicTacToe()
    while not game.isFinished():

        # TODO track stats?

        if game.isOurTurn():
            try:
                pickAndMakeMove(game, opponent)
            except:
                # Penalise player
                return -100.0

            try:
                pickAndMakeMove(game, opponent)
            except:
                pickAndMakeMove(game, RandomAgent())
        else: # Not our turn
            try:
                pickAndMakeMove(game, opponent)
            except:
                pickAndMakeMove(game, RandomAgent())

            try:
                pickAndMakeMove(game, opponent)
            except:
                # Penalise player
                return -100.0

    # Game is finished (or illegal move made)

    # TODO debug prints, or stats

    return game.score()

def eval_genome(genome, config):
    genome.fitness = 0.0
    player = neat.nn.FeedForwardNetwork.create(genome, config)
    opponent = agents.RandomAgent()

    # TODO loop through some number of games
    #      maybe do markov selection whatevs?
    #
    # - In loop, simulateGame
    # - finally avg the fitness, print out stats?

    genome.fitness += simulateGame(player, opponent)

    # TODO also want to track who is our opponent
    #      or do we want to have that done in bunches
    #      i.e. we should pick best/worst/random ai to be opponent?
    #      or multiple?

    # TODO think about fitness RE perfect players playing each others

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
    p.add_reporter(neat.Checkpointer(5))

    # TODO parallelise 

    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 300)

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
