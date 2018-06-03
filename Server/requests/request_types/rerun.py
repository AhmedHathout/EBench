from threading import Event, Thread

from lib.my_pickle import MyPickle
from Server.job.configuration import Configuration
from Server.job.job import Job
from Server.problems.problem import Problem
from Server.requests.request import Request
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate
from libraries_paths.libraries_functions import *


class Rerun(Request):

    def __init__(self, pickle:MyPickle, job_id: str,
                 maximum_problems_in_parallel: str, job_id_lock: Event,
                 running_jobs: [Job], running_jobs_lock: Event, **kwargs):

        super().__init__(pickle)
        self.job_id = job_id
        self.maximum_problems_in_parallel = maximum_problems_in_parallel
        self.job_id_lock = job_id_lock
        self.running_jobs_lock = running_jobs_lock
        self.running_jobs = running_jobs

    def execute(self):

        output = Job.get_job_stage(self.job_id, self.running_jobs)

        if isinstance(output, Job):
            error = Error("This job is already running")
            self.pickle.send(error.create_dictionary())

        elif output:
            try:
                with open(get_job_report(self.job_id), "r") as f:
                    prover_options = f.readline().split("\t")[1].strip()
                    prover_id = f.readline().split("\t")[1].strip()

            except FileNotFoundError as e:
                self.pickle.send(Error(str(e)).create_dictionary())

            else:
                configuration = Configuration(prover_options, prover_id)
                try:
                    configuration.verify_prover()

                except OSError as e:
                    self.pickle.send(Error(str(e)).create_dictionary())

                else:
                    problems = Problem.get_problems_from_report(self.job_id)

                    try:
                        job = Job(problems, configuration,
                                  self.maximum_problems_in_parallel,
                                  self.running_jobs, self.running_jobs_lock,
                                  self.job_id_lock, self.job_id)

                        run_job_thread = Thread(name="run_job", target=job.run)
                        run_job_thread.start()

                    except ValueError as e:
                        self.pickle.send(Error(str(e)).create_dictionary())

                    else:
                        success = Success("Job" + str(self.job_id) + " was resubmitted")
                        self.pickle.send(success.create_dictionary())
                        self.pickle.send(Terminate().create_dictionary())

        else:
            error = Error("No such job with that id: " + self.job_id)
            self.pickle.send(error.create_dictionary())
