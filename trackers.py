from neat.reporting import BaseReporter
from agents import RandomAgent

class OpponentTracker(BaseReporter):

    def __init__(self):
        self._generations = 0
        self._best_genome = None
        self._get_random_opponent()

    def post_evaluate(self, config, population, species, best_genome):
        if self._best_genome is None or best_genome.fitness > self._best_genome.fitness:
            self._best_genome = best_genome

    @property
    def current_opponent(self):
        if self._current_opponent is None:
            return self._get_random_opponent()
        return self._current_opponent

    def get_new_opponent(self):
        if self._best_genome is None:
            return self._get_random_opponent()
        self._current_opponent = self._best_genome
        self._best_genome = None
        return self._current_opponent

    def _get_random_opponent(self):
        self._current_opponent = RandomAgent()
        return self._current_opponent
