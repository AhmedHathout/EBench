import os
from lib.my_pickle import MyPickle
from Server.job.job import Job
from Server.requests.request import Request
from server_response.response_types.send import Send
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class KillJob(Request):
    """A class used to kill the scheduled problem in some job."""

    def __init__(self, pickle:MyPickle, job_id: str,
                 running_jobs: [Job], **kwargs):
        """Create a new object.

                Args:
                    pickle: Used to send and receive messages.
                    job_id: The ID of the job that is required to know its status.
                    running_jobs: A list of all the running jobs.
                """

        super().__init__(pickle)
        self.job_id = job_id
        self.running_jobs = running_jobs

    def execute(self):

        # Get the stage of the job; running, finished or does not exist at all.
        output = Job.get_job_stage(self.job_id, self.running_jobs)

        # Check if it is running.
        if isinstance(output, Job):

            # Kill the job.
            output.kill()

            #Create a success object informing the client that no errors
            # happened, send it and tell the client to accept a new request
            # from the user.
            success = Success("Job" + str(self.job_id) + " was killed")
            self.pickle.send(success.create_dictionary())
            self.pickle.send(Terminate().create_dictionary())

        # If it is not a job then it is either True or False.
        elif output:
            # Send a message to the client informing it that it has already
            # finished.
            success = Success("This job has already finished")
            self.pickle.send(success.create_dictionary())
            self.pickle.send(Terminate().create_dictionary())

        else:
            # Send an error message to the client informing it that the
            # required job does not exist.
            error = Error("No such job with that id: " + self.job_id)
            self.pickle.send(error.create_dictionary())
