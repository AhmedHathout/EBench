from abc import ABC, abstractmethod

from Server.problems.problem import Problem


class State(ABC):

    def __init__(self, problem: Problem):
        self.problem = problem

    @abstractmethod
    def run(self, configuration):
        pass

    @abstractmethod
    def remove(self):
        pass
