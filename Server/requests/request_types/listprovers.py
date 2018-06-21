import json

import os

from lib.my_pickle import MyPickle
from Server.job.job import Job
from Server.requests.request import Request
from libraries_paths.libraries_paths import provers_library
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class ListProvers(Request):

    def __init__(self, pickle:MyPickle, **kwargs):
        super().__init__(pickle)

    def execute(self):
        provers = sorted([prover[1:] for prover in os.listdir(provers_library)])
        if not provers:
            message = "No provers found!"
        else:
            message = "Here is a list of the ids of the provers:-\n" + \
                "\n".join(provers)

        success = Success(message)
        self.pickle.send(success.create_dictionary())
        self.pickle.send(Terminate().create_dictionary())