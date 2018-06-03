import subprocess

from Server.job.configuration import Configuration
from Server.problems.problem import Problem
from Server.problems.state import State
from Server.problems.state_types.removed import Removed
from Server.problems.state_types.running import Running
from libraries_paths.libraries_functions import get_prover_bin


class Scheduled(State):

    def __init__(self, problem: Problem):
        super().__init__(problem)

    def run(self, configuration: Configuration):
        command = "./eprover " + configuration.prover_options + \
                  " " + self.problem.path

        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=get_prover_bin(configuration.prover_id),
                                   shell=True,
                                   universal_newlines=True)

        self.problem.set_state(Running)

        return process

    def remove(self):
        self.problem.set_state(Removed)
