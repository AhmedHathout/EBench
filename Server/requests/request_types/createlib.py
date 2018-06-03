import os

from lib.my_pickle import MyPickle
from libraries_paths.libraries_paths import server_problems_library
from Server.requests.request import Request
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class CreateLib(Request):

    def __init__(self, pickle: MyPickle, directory: str, **kwargs):
        super().__init__(pickle)
        self.directory = directory

    def execute(self):
        try:
            os.makedirs(server_problems_library + self.directory)

        except OSError as e:
            self.pickle.send(Error(str(e)).create_dictionary())

        else:
            success_message = "Library " + self.directory + \
                              " was created successfully"
            success = Success(success_message)
            success_dictionary = success.create_dictionary()

            self.pickle.send(success_dictionary)

            terminate = Terminate()
            terminate_dictionary = terminate.create_dictionary()

            self.pickle.send(terminate_dictionary)
