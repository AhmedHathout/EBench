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

    def __init__(self, pickle:MyPickle, job_id: str,
                 running_jobs: [Job], delimiter="\t", **kwargs):

        super().__init__(pickle)
        self.job_id = job_id
        self.running_jobs = running_jobs

    def execute(self):

        output = Job.get_job_stage(self.job_id, self.running_jobs)

        if isinstance(output, Job):
            job_status = output.get_status(Job.format_status,
                                           **{"delimiter": "\t"})
            success = Success(job_status)
            self.pickle.send(success.create_dictionary())
            self.pickle.send(Terminate().create_dictionary())

        elif output:
            success = Success("This job has already finished")
            self.pickle.send(success.create_dictionary())
            self.pickle.send(Terminate().create_dictionary())

        else:
            error = Error("No such job with that id: " + str(self.job_id))
            self.pickle.send(error.create_dictionary())

