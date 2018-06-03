from Server.problems.problem import Problem
from Server.problems.state import State


class Error(State):

    def __init__(self, problem: Problem):
        super().__init__(problem)
        self.error_message = "this problem '" + self.problem.path + \
                             "' has already been run and gave and error"

    def run(self, configuration):
        raise ValueError(self.error_message)

    def remove(self):
        raise ValueError(self.error_message)
