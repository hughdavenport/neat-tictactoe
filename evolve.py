from __future__ import print_function
import neat
import pickle       # pip install cloudpickle

def eval_genome(genome, config):
    genome.fitness = 0.0
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # TODO loop through some number of games
    #      maybe do markov selection whatevs?
    #
    # - In loop
    #  - while game isn't finished
    #   - if it is our turn
    #    - activate net and make a choice
    #     * NB, if choice is illegal, penalise heavily?
    #    - get current opponent to do the same
    #   - otherwise do the opposite order
    #  - adjust fitness
    # - finally avg the fitness, print out stats?

    # TODO also want to track who is our opponent
    #      or do we want to have that done in bunches

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
