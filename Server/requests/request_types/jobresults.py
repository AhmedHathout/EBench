from lib.my_pickle import MyPickle
from libraries_paths.libraries_functions import *
from Server.job.job import Job
from Server.requests.request import Request
from server_response.response_types.receive import Receive
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class JobResults(Request):
    """Used to send the results of a job to the client."""

    def __init__(self, pickle:MyPickle, client_libraries: {str, str},
                 job_id: str, running_jobs: [Job], **kwargs):
        """Create a new object.

        Args:
            pickle: Used to send and receive messages.
            running_jobs: A list of all the running jobs.
            job_id: The ID of the job that is required to know its resutls.
        """
        super().__init__(pickle)
        self.job_id = job_id
        self.client_results_library = client_libraries["results"]
        self.running_jobs = running_jobs

    def execute(self):

        # Get the stage of the job; running, finished or does not exist at all.
        output = Job.get_job_stage(self.job_id, self.running_jobs)

        # If it is running, then output is the job, if it finished then output
        # Is true. In any of these two cases, the results folder can be sent.
        if output:

            # Create an instance from receive and send it to the client
            # infroming it that the server is going to send the results folder.
            # Also Tell the client to save it in the results library by adding
            # its path in Receive.
            receive = Receive(pickle=None, path=self.client_results_library)
            self.pickle.send(receive.create_dictionary())

            # Get the path of the results folder on the server.
            server_path = get_server_job_results_path_by_id(self.job_id)

            # Send it.
            self.pickle.send_folder(server_path, server_jobs_results_library)

            # Send a success message to the client.
            success = Success("Job{} results folder was sent successfully".
                              format(self.job_id))

            # Tell the client to accept new requests from the user.
            self.pickle.send(success.create_dictionary())
            self.pickle.send(Terminate().create_dictionary())

        else:
            error = Error("No such job with that id: " + self.job_id)
            self.pickle.send(error.create_dictionary())
