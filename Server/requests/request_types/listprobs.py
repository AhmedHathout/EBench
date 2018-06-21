import json

import os

from lib.my_pickle import MyPickle
from Server.job.job import Job
from Server.requests.request import Request
from libraries_paths.libraries_paths import provers_library, \
    server_problems_library
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class ListProbs(Request):

    def __init__(self, pickle:MyPickle, recursive: bool, **kwargs):
        super().__init__(pickle)
        self.recursive = recursive

    def execute(self):
        if self.recursive:
            libraries = []
            for root, folders, files_ in os.walk(server_problems_library):
                for folder in folders:
                    libraries.append(os.path.join(root, folder))

        else:
            # libraries = [os.path.join(server_problems_library, library)
            #              for library in os.listdir(server_problems_library)]
            libraries = os.listdir(server_problems_library)

        if libraries:
            message = "Here is a list of the libraries:-\n- " + \
                      "\n- ".join(libraries)

        else:
            message = "No libraries found!"

        success = Success(message)
        self.pickle.send(success.create_dictionary())
        self.pickle.send(Terminate().create_dictionary())
