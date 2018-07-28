from lib.my_pickle import MyPickle
from libraries_paths.libraries_functions import *
from Server.job.job import Job
from Server.requests.request import Request
from server_response.response_types.receive import Receive
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.terminate import Terminate


class JobReport(Request):
    """Used to send the report of a job to the client."""

    def __init__(self, pickle:MyPickle, client_libraries: {str:str}, job_id: str,
                 running_jobs: [Job], **kwargs):
        """Create a new object.

        Args:
            pickle: Used to send and receive messages.
            running_jobs: A list of all the running jobs.
            job_id: The ID of the job that is required to know its report.
        """

        super().__init__(pickle)
        self.job_id = job_id
        self.client_reports_library = client_libraries["reports"]
        self.running_jobs = running_jobs

    def execute(self):

        # Get the stage of the job; running, finished or does not exist at all.
        output = Job.get_job_stage(self.job_id, self.running_jobs)

        # Check if the job is still running.
        if isinstance(output, Job):
            # - Still running.
            # - Then there is no report generated yet. Inform the client.
            self.pickle.send(Error("Job is still running").create_dictionary())

        # Finished
        elif output:

            # Great, tell the client to be prepared to receive the folder.
            receive = Receive(pickle=None, path=self.client_reports_library)
            self.pickle.send(receive.create_dictionary())

            # Get the path to the results folder.
            server_path = get_server_job_report_path_by_id(self.job_id)

            # Send it.
            self.pickle.send_folder(server_path, server_jobs_reports_library)

            # client, you can accept the next request from the user, buddy.
            self.pickle.send(Terminate().create_dictionary())

        else:
            # No job was that ID, dude.
            error = Error("No such job with that id: " + self.job_id)
            self.pickle.send(error.create_dictionary())
