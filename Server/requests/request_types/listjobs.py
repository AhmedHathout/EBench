import json
from lib.my_pickle import MyPickle
from Server.job.job import Job
from Server.requests.request import Request
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class ListJobs(Request):
    """List all jobs that were submitted whether running or finished."""

    def __init__(self, pickle:MyPickle, running_jobs: [Job], **kwargs):
        """Create a new object.

        Args:
            pickle: Used to send and receive messages.
            running_jobs: A list of all the running jobs.
        """
        super().__init__(pickle)
        self.running_jobs = running_jobs

    def execute(self):

        # Get details about all the jobs then convert them into a json string.
        data = Job.list_jobs(self.running_jobs, json.dumps, indent=2,
                             sort_keys=True, default=lambda x: x.__dict__)

        if not data:

            # -No data was found.
            # -Make the success message say that there are neither running nor
            # finished jobs.
            success = Success("No running or finished jobs to list!")
        else:
            # Create a success instance with data being its message.
            success = Success(data)

        # Send the success message to the client.
        self.pickle.send(success.create_dictionary())
        self.pickle.send(Terminate().create_dictionary())
