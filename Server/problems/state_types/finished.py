from Server.problems.problem import Problem
from Server.problems.state import State


class Finished(State):

    def __init__(self, problem: Problem):
        super().__init__(problem)
        self.message = "this problem '" + self.problem.path + \
                       "' has alredy finished"

    def run(self, configuration):
        raise ValueError(self.message)

    def remove(self):
        raise ValueError(self.message)
