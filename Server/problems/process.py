from Server.job.configuration import Configuration
from Server.problems.problem import Problem


class Process(object):

    def __init__(self, problem: Problem):
        self.problem = problem
        self.process = None

    def run(self, configuration: Configuration) -> None:
        self.process = self.problem.run(configuration)

    def write_results(self, save_to: str) -> (str, str):
        data, error = self.process.communicate()
        self.problem.set_results(data, error, save_to)