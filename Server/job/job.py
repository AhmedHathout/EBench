import os
import shutil
import subprocess
from datetime import datetime
from multiprocessing import cpu_count
from threading import Event

from lib.directory import directorize
from libraries_paths.libraries_functions import *
from Server.job.configuration import Configuration
from Server.problems.problem import Problem
from Server.problems.process import Process
from Server.problems.state_types.error import Error
from Server.problems.state_types.finished import Finished
from Server.problems.state_types.removed import Removed
from Server.problems.state_types.running import Running
from Server.problems.state_types.scheduled import Scheduled


class Job(object):

    def __init__(self, problems: [Problem], configuration: Configuration,
                 maximum_problems_in_parallel: str, running_jobs: [],
                 running_jobs_lock: Event, job_id_lock: Event, id=None):

        self.job_id_lock = job_id_lock
        self.id = id if id else self.get_next_id()
        self.problems = problems
        self.configuration = configuration
        self.maximum_problems_in_parallel = \
            int(maximum_problems_in_parallel) if \
                maximum_problems_in_parallel else cpu_count()

        self.running_jobs = running_jobs
        self.running_jobs_lock = running_jobs_lock
        self.save_results_to = get_server_job_results_path_by_id(self.id)
        self.save_reports_to = get_server_job_report_path_by_id(self.id)
        self.submission_time = datetime.now()

    def run(self):

        self.running_jobs_lock.wait()
        self.running_jobs.append(self)
        self.running_jobs_lock.set()

        processes = []
        problems_checked = 0

        for problem in self.problems:
            if len(processes) >= self.maximum_problems_in_parallel:
                break

            process = Process(problem)

            try:
                process.run(self.configuration)
                processes.append(process)
            except ValueError:
                pass
            finally:
                problems_checked += 1

        for process in processes:
            process.write_results(self.save_results_to)

            if problems_checked < len(self.problems):
                process = Process(self.problems[problems_checked])

                try:
                    process.run(self.configuration)
                    processes.append(process)
                except ValueError:
                    pass
                finally:
                    problems_checked += 1

        self.write_report()

        self.running_jobs_lock.wait()
        self.running_jobs.remove(self)
        self.running_jobs_lock.set()

    def kill(self):
        for problem in self.problems:
            try:
                problem.remove()
            except ValueError:
                pass

    def get_status(self):
        status = {Scheduled.__name__: 0,
                  Running.__name__: 0,
                  Finished.__name__: 0,
                  Error.__name__: 0,
                  Removed.__name__: 0}

        for problem in self.problems:
            status[type(problem.state).__name__] += 1

        total = len(self.problems)
        result = ("Scheduled = " + str(status[Scheduled.__name__]) + " = " + str(status[Scheduled.__name__] * 100 / total) + "%\n" +
                "Running = " + str(status[Running.__name__]) + " = " + str(status[Running.__name__] * 100/ total) + "%\n" +
                "Finished = " + str(status[Finished.__name__]) + " = " + str(status[Finished.__name__] * 100/ total) + "%\n")

        if status[Removed.__name__] > 0:
            result += "Removed = " + str(status[Removed.__name__]) + " = " + str(status[Removed.__name__] * 100/ total) + "%\n"

        if status[Error.__name__] > 0:
            result += "Error = " + str(status[Error.__name__]) + " = " + str(status[Error.__name__] * 100/ total) + "%\n"

        return result.strip()


    def write_report(self):
        if os.path.exists(self.save_reports_to):
            shutil.rmtree(self.save_reports_to)

        os.makedirs(self.save_reports_to)

        report_path = self.save_reports_to + "Job" + str(self.id)
        prover_options = self.configuration.prover_options
        prover_id = self.configuration.prover_id

        command = "./genprot.py --delimiter='\t' --saveto=" + report_path + \
                  " --prover-id=" + prover_id + " --prover-options='" + \
                  prover_options + "' " + self.save_results_to

        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True,
                                   cwd="./job/",
                                   universal_newlines=True)
        process.communicate()

        failed_problems = self.get_problems_by_state(Error)
        removed_problems = self.get_problems_by_state(Removed)

        if failed_problems:
            with open(self.save_reports_to + "failed_problems.tsv", "w") as f:
                f.write("Problem\tError\n")
                for problem in failed_problems:
                    f.write(problem.path + "\t" + problem.result_error.replace("\n", ". ") + "\n")

        if removed_problems:
            with open(self.save_reports_to + "removed_problems.txt", "w") as f:
                for problem in removed_problems:
                    f.write(problem.path + "\n")

    def get_problems_by_state(self, state: type):
        problems = []

        for problem in self.problems:
            if type(problem.state) == state:
                problems.append(problem)

        return problems

    def get_details(self):
        details = str(self.id) + "\t" + \
                  self.get_status().replace("\n", ", ")[:-1] + "\t" + \
                  str(self.submission_time) + "\t" + str(len(self.problems)) + \
                  "\t" + self.configuration.prover_id + "\t" + \
                  self.configuration.prover_options

        return details

    @staticmethod
    def get_problems_from_library(path: str, problems=[]):
        if not os.path.isdir(path):
            raise ValueError("No library with that path: " + path)
        for item in os.listdir(path):
            if os.path.isdir(item):
                Job.get_problems_from_library(path + directorize(item), problems)
            else:
                if item.endswith(Problem.problems_extensions):
                    problems.append(Problem(
                        "/" + directorize(os.path.abspath(path)) + item))

        return problems

    @staticmethod
    def get_job_by_id(job_id: str, running_jobs: []):
        for job in running_jobs:
            if job.id == job_id:
                return job

    @staticmethod
    def get_job_stage(job_id: str, running_jobs: []):
        job = Job.get_job_by_id(job_id, running_jobs)

        if job:
            return job

        else:
            results_path = get_server_job_results_path_by_id(job_id)
            if os.path.isdir(results_path):
                return True

            else:
                return False

    def get_next_id(self):
        self.job_id_lock.wait()
        id = 1

        while True:
            try:
                path_to_results = get_server_job_results_path_by_id(id)
                os.makedirs(path_to_results)
                self.job_id_lock.set()
                return id

            except OSError:
                id += 1
