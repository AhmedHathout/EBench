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
    """Rerun a previously killed job."""

    def __init__(self, pickle:MyPickle, job_id: str,
                 maximum_problems_in_parallel: str, job_id_lock: Event,
                 running_jobs: [Job], running_jobs_lock: Event, **kwargs):

        """Create a new object.

        Args:
            pickle: Used to send and receive messages.
            job_id: The ID of the job that is to be rerun.
            maximum_problems_in_parallel: The number of problems allowed to
                                          run in parrallel in the job.
            job_id_lock: Lock to ID generator.
            running_jobs: List of all the running jobs.
            running_jobs_lock: Lock to that list.
        """
        super().__init__(pickle)
        self.job_id = job_id
        self.maximum_problems_in_parallel = maximum_problems_in_parallel
        self.job_id_lock = job_id_lock
        self.running_jobs_lock = running_jobs_lock
        self.running_jobs = running_jobs

    def execute(self):

        # Get the stage of the job; running, finished or does not exist at all.
        output = Job.get_job_stage(self.job_id, self.running_jobs)

        # Check if it is running.
        if isinstance(output, Job):

            # Send and error to the client since a job can not be rerun if it
            # is already running.
            error = Error("This job is already running")
            self.pickle.send(error.create_dictionary())


        elif output:

            # It has finished. Try to open the report. surrounding it with try
            # and catch is an extra precaution.
            try:
                with open(get_job_report(self.job_id), "r") as f:

                    # Get the prover options from the report.
                    prover_options = f.readline().split("\t")[1].strip()

                    # Get the prover ID from the report.
                    prover_id = f.readline().split("\t")[1].strip()

            except FileNotFoundError as e:
                # Report was not found. Inform the client.
                self.pickle.send(Error(str(e)).create_dictionary())

            else:

                # Make a new configuration object using the options and ID.
                configuration = Configuration(prover_options, prover_id)

                # Check if the prover exists.
                try:
                    configuration.verify_prover()

                except OSError as e:
                    self.pickle.send(Error(str(e)).create_dictionary())

                else:

                    # Get all the problems that failed or were removed.
                    problems = Problem.get_problems_from_report(self.job_id)

                    try:

                        # Create a job object.
                        job = Job(problems, configuration,
                                  self.maximum_problems_in_parallel,
                                  self.running_jobs, self.running_jobs_lock,
                                  self.job_id_lock, self.job_id)

                        # Create a thread to run that job and run it.
                        run_job_thread = Thread(name="run_job", target=job.run)
                        run_job_thread.start()

                    except ValueError as e:

                        # -Could not create a job.
                        # -Send the error to the client.
                        self.pickle.send(Error(str(e)).create_dictionary())

                    else:

                        # Send a success message to the client.
                        success = Success("Job" + str(self.job_id) + " was resubmitted")
                        self.pickle.send(success.create_dictionary())
                        self.pickle.send(Terminate().create_dictionary())

        else:
            # No job with that ID. Send that to the client.
            error = Error("No such job with that id: " + self.job_id)
            self.pickle.send(error.create_dictionary())
