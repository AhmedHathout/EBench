from lib.my_pickle import MyPickle
from libraries_paths.libraries_functions import *
from Server.job.job import Job
from Server.requests.request import Request
from server_response.response_types.receive import Receive
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.terminate import Terminate


class JobReport(Request):

    def __init__(self, pickle:MyPickle, job_id: str,
                 running_jobs: [Job], **kwargs):

        super().__init__(pickle)
        self.job_id = job_id
        self.running_jobs = running_jobs

    def execute(self):

        output = Job.get_job_stage(self.job_id, self.running_jobs)

        if isinstance(output, Job):
            self.pickle.send(Error("Job is still running").create_dictionary())

        elif output:
            receive = Receive(pickle=None, path=client_jobs_reports_library)
            self.pickle.send(receive.create_dictionary())

            server_path = get_server_job_report_path_by_id(self.job_id)
            self.pickle.send_folder(server_path, server_jobs_reports_library)

            self.pickle.send(Terminate().create_dictionary())

        else:
            error = Error("No such job with that id: " + self.job_id)
            self.pickle.send(error.create_dictionary())
