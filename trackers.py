from neat.reporting import BaseReporter
from neat.nn import FeedForwardNetwork
from agents import RandomAgent

class OpponentTracker(BaseReporter):

    def __init__(self, reset_number=10):
        self._generations = 0
        self._best_net = None
        self._best_fitness = None
        self._reset_number = reset_number
        self._current_opponent = RandomAgent()
        self._last_fitness = None

    def post_evaluate(self, config, population, species, best_genome):
        if self._best_net is None or best_genome.fitness > self._best_fitness:
            self._best_net = FeedForwardNetwork.create(best_genome, config)
            self._best_fitness = best_genome.fitness
        print("Best fitness so far", self._best_fitness, ", Currently used agent:", "random" if self._last_fitness is None else self._last_fitness)
        self._generations += 1
        if self._generations >= self._reset_number:
            is_random = self._last_fitness is not None and self._best_fitness < self._last_fitness
            print("Resetting opponent, last fitness was",
                    "random" if self._last_fitness is None else self._last_fitness,
                    "new fitness is",
                    "random" if is_random else self._best_fitness)
            if is_random:
                self._current_opponent = RandomAgent()
                self.last_fitness = None
            else:
                self._current_opponent = self._best_net
                self._last_fitness = self._best_fitness
                self._best_fitness = None
                self._best_net = None
            self._generations = 0

    @property
    def current_opponent(self):
        return self._current_opponent
