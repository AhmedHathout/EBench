from Server.problems.problem import Problem
from Server.problems.state import State


class Removed(State):

    def __init__(self, problem: Problem):
        super().__init__(problem)

    def run(self, configuration):
        raise ValueError("this problem '" + self.problem.path + "' was removed")

    def remove(self):
        raise ValueError("this problem '" + self.problem.path +
                         "' was removed before")
