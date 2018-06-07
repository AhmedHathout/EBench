import os
import shutil
import subprocess
from datetime import datetime
from multiprocessing import cpu_count
from threading import Event
import json

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
        self.save_report_to = get_server_job_report_path_by_id(self.id)
        self.save_details_to = get_server_job_details_file_by_id(self.id)
        self.submission_time = datetime.now().__str__()
        self.finish_time = None

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

        def __finish(job: Job):
            job.finish_time = datetime.now().__str__()
            job.write_data()
            job.write_report()
            job.running_jobs_lock.wait()
            job.running_jobs.remove(job)
            job.running_jobs_lock.set()

        __finish(self)

    def write_data(self):
        os.makedirs(server_jobs_details_library, exist_ok=True)
        data = self.__dict__.copy()

        data = Job.prepare_job_dictionary(data)

        with open(self.save_details_to, "w") as f:
            json.dump(data, f, default=lambda value: value.__dict__, indent=2)

    def kill(self):
        for problem in self.problems:
            try:
                problem.remove()
            except ValueError:
                pass

    def get_status(self, callback=None, **kwargs):
        status = {Scheduled.__name__: 0,
                  Running.__name__: 0,
                  Finished.__name__: 0,
                  Error.__name__: 0,
                  Removed.__name__: 0}

        for problem in self.problems:
            status[type(problem.state).__name__] += 1

        return callback(status, **kwargs) if callback else status


    @staticmethod
    def format_status(status: {str: int}, delimiter: str):
        s = ""
        return "".join([s + "{} = {}{}".format(key, value, delimiter)
                        for key, value in status.items()])

    def write_report(self):
        if os.path.exists(self.save_report_to):
            shutil.rmtree(self.save_report_to)

        os.makedirs(self.save_report_to)

        report_path = self.save_report_to + "Job" + str(self.id)
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
            with open(self.save_report_to + "failed_problems.tsv", "w") as f:
                f.write("Problem\tError\n")
                for problem in failed_problems:
                    f.write(problem.path + "\t" + problem.result_error.replace("\n", ". ") + "\n")

        if removed_problems:
            with open(self.save_report_to + "removed_problems.txt", "w") as f:
                for problem in removed_problems:
                    f.write(problem.path + "\n")

    def get_problems_by_state(self, state: type):
        problems = []

        for problem in self.problems:
            if type(problem.state) == state:
                problems.append(problem)

        return problems

    @staticmethod
    def get_details(running_jobs: [], callback=None, **kwargs):
        os.makedirs(server_jobs_details_library, exist_ok=True)

        finished_jobs_details = []
        for item in os.listdir(server_jobs_details_library):
            with open(server_jobs_details_library + item, "r") as f:
                finished_jobs_details.append(json.load(f))

        running_jobs_details = []

        for job in running_jobs:
            data = Job.prepare_job_dictionary(job.__dict__.copy())
            data.update({"problems" : job.get_status()})
            running_jobs_details.append(data)

        all_jobs_details = running_jobs_details + finished_jobs_details
        all_jobs_details.sort(key=lambda x: x["id"])

        return callback(all_jobs_details, **kwargs) if callback \
            else (running_jobs, finished_jobs_details)

    @staticmethod
    def list_jobs(running_jobs, callback=None, **kwargs):
        return Job.get_details(running_jobs, callback,
                               **kwargs)

    @staticmethod
    def prepare_job_dictionary(data: dict):
        keys_to_delete = ("job_id_lock",
                          "problems",
                          "save_report_to",
                          "save_results_to",
                          "running_jobs",
                          "running_jobs_lock",
                          "save_details_to")

        for key in keys_to_delete:
            del data[key]

        return data

    @staticmethod
    def get_problems_from_library(path: str, problems: [Problem]):
        if not os.path.isdir(path):
            raise ValueError("No library with that path: " + path)
        for item in os.listdir(path):
            new_path = directorize(path) + directorize(item)
            if os.path.isdir(new_path):
                Job.get_problems_from_library(new_path, problems)
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
