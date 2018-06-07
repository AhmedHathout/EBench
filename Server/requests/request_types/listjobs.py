import json
from lib.my_pickle import MyPickle
from Server.job.job import Job
from Server.requests.request import Request
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class ListJobs(Request):

    def __init__(self, pickle:MyPickle, running_jobs: [Job], delimiter="\t",
                 **kwargs):

        super().__init__(pickle)
        self.running_jobs = running_jobs
        self.delimiter = delimiter

    def execute(self):
        data = Job.list_jobs(self.running_jobs, json.dumps, indent=2,
                             sort_keys=True, default=lambda x: x.__dict__)

        if not data:
            success = Success("No running or finished jobs to list!")
        else:
            success = Success(data)

        self.pickle.send(success.create_dictionary())
        self.pickle.send(Terminate().create_dictionary())
