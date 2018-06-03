import os
from lib.my_pickle import MyPickle
from Server.job.job import Job
from Server.requests.request import Request
from server_response.response_types.send import Send
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class KillJob(Request):

    def __init__(self, pickle:MyPickle, job_id: str,
                 running_jobs: [Job], **kwargs):

        super().__init__(pickle)
        self.job_id = job_id
        self.running_jobs = running_jobs

    def execute(self):

        output = Job.get_job_stage(self.job_id, self.running_jobs)

        if isinstance(output, Job):
            output.kill()
            success = Success("Job" + str(self.job_id) + " was killed")
            self.pickle.send(success.create_dictionary())
            self.pickle.send(Terminate().create_dictionary())

        elif output:
            success = Success("This job has already finished")
            self.pickle.send(success.create_dictionary())
            self.pickle.send(Terminate().create_dictionary())

        else:
            error = Error("No such job with that id: " + self.job_id)
            self.pickle.send(error.create_dictionary())
