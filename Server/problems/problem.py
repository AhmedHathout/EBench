import os

from Server.job.configuration import Configuration
from lib.directory import directorize
from libraries_paths.libraries_functions import *


class Problem(object):

    problems_extensions = (".p", ".tptp", ".lop")

    def __init__(self, path: str):
        self.path = path
        from Server.problems.state_types.scheduled import Scheduled
        self.state = Scheduled(self)
        self.result_data = None
        self.result_error = None

    def run(self, configuration: Configuration):
        return self.state.run(configuration)

    def set_state(self, state: type):
        self.state = state(self)

    def remove(self):
        self.state.remove()

    def set_results(self, data: str, error: str, save_to: str) -> None:
        self.result_data = data
        self.result_error = error

        if self.result_error:
            from Server.problems.state_types.error import Error
            self.state = Error(self)
            return

        from Server.problems.state_types.finished import Finished
        self.state = Finished(self)

        save_to += self.path_to_write()
        os.makedirs(save_to, exist_ok=True)

        with open(save_to + self.get_name() + ".txt", "w") as f:
            f.write("% Problem\t: " + self.get_name_without_extension() + "\n")
            f.write(self.result_data)

    def path_to_write(self) -> str:
        return ".".join(self.path.replace(server_problems_library, "").split(".")[:-1]) + "/"

    def get_name(self) -> str:
        return self.path.split("/")[-1]

    def get_name_without_extension(self) -> str:
        return self.get_name().split(".")[0]

    @staticmethod
    def get_problems_from_report(job_id):
        problems = []
        removed_problems = []
        failed_problems = []

        path = get_server_removed_problems_from_job(job_id)
        if os.path.isfile(path):
            with open(path, "r") as f:
                removed_problems = [Problem(line.strip()) for line in
                                    f.readlines()]

        path = get_server_failed_problems_from_job(job_id)
        if os.path.isfile(path):
            with open(path, "r") as f:
                failed_problems = [Problem(line.strip().split("\t")[0].strip())
                                   for line in f.readlines()[1:]]

        problems.extend(removed_problems)
        problems.extend(failed_problems)

        return problems