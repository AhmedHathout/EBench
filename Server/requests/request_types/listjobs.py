import os
from lib.my_pickle import MyPickle
from Server.job.job import Job
from Server.requests.request import Request
from server_response.response_types.send import Send
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class ListJobs(Request):

    def __init__(self, pickle:MyPickle, running_jobs: [Job], **kwargs):
        super().__init__(pickle)
        self.running_jobs = running_jobs

    def execute(self):
        running_jobs_details = ""
        for job in self.running_jobs:
            running_jobs_details += job.get_details() + "\n"

        if running_jobs_details:
            success = Success("Here is a list of the running jobs:-\n" +
                              running_jobs_details)
            self.pickle.send(success.create_dictionary())
        else:
            self.pickle.send(Success("No running jobs!").create_dictionary())

        self.pickle.send(Terminate().create_dictionary())
