import os
from threading import Event, Thread

from lib.my_pickle import MyPickle
from Server.job.configuration import Configuration
from Server.job.job import Job
from Server.requests.request import Request
from libraries_paths.libraries_paths import server_problems_library
from server_response.response_types.send import Send
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class SubJob(Request):

    def __init__(self, pickle: MyPickle, prover_options: str, prover_id: str,
                 maximum_problems_in_parallel: str, problems_path: str,
                 running_jobs: [Job], running_jobs_lock: Event(), job_id_lock: Event):

        super().__init__(pickle)
        self.configuration = Configuration(prover_options, prover_id)
        self.maximum_problems_in_parallel = maximum_problems_in_parallel
        self.problems_path = server_problems_library + problems_path
        self.running_jobs = running_jobs
        self.running_jobs_lock = running_jobs_lock
        self.job_id_lock = job_id_lock

    def execute(self):
        try:
            self.configuration.verify_prover()
        except OSError as e:
            self.pickle.send(Error(str(e)).create_dictionary())
        else:
            problems = Job.get_problems_from_library(self.problems_path)

            try:
                job = Job(problems, self.configuration,
                          self.maximum_problems_in_parallel, self.running_jobs,
                          self.running_jobs_lock, self.job_id_lock)

            except ValueError as e:
                self.pickle.send(Error(str(e)).create_dictionary())

            else:
                run_job_thread = Thread(name="run_job", target=job.run)
                run_job_thread.start()

                success = Success("Job submitted with id: " + str(job.id))
                self.pickle.send(success.create_dictionary())

                self.pickle.send(Terminate().create_dictionary())