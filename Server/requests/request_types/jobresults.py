from lib.my_pickle import MyPickle
from libraries_paths.libraries_functions import *
from Server.job.job import Job
from Server.requests.request import Request
from server_response.response_types.status.receive import Receive
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class JobResults(Request):

    def __init__(self, pickle:MyPickle, job_id: str,
                 running_jobs: [Job], **kwargs):

        super().__init__(pickle)
        self.job_id = job_id
        self.running_jobs = running_jobs

    def execute(self):

        output = Job.get_job_stage(self.job_id, self.running_jobs)

        if output:
            receive = Receive(pickle=None, path=client_jobs_results_library)
            self.pickle.send(receive.create_dictionary())

            server_path = get_server_job_results_path_by_id(self.job_id)
            self.pickle.send_folder(server_path, server_jobs_results_library)

            self.pickle.send(Terminate().create_dictionary())

        else:
            error = Error("No such job with that id: " + self.job_id)
            self.pickle.send(error.create_dictionary())
