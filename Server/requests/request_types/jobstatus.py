import os
from lib.my_pickle import MyPickle
from libraries_paths.libraries_functions import get_server_job_results_path_by_id
from Server.job.job import Job
from Server.requests.request import Request
from server_response.response_types.send import Send
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class JobStatus(Request):
    """A class used to send a string containing the status of a job."""

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

            # Get its status.
            job_status = output.get_status(Job.format_status,
                                           **{"delimiter": "\t"})

            # Create a success object with the status being its message, send
            # it and tell the client to accept the new request from the user.
            success = Success(job_status)
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
            error = Error("No such job with that id: " + str(self.job_id))
            self.pickle.send(error.create_dictionary())

