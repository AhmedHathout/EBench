import os
from lib.my_pickle import MyPickle
from Server.requests.request import Request
from server_response.response_types.send import Send
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate
from libraries_paths.libraries_paths import *


class AddProbs(Request):

    def __init__(self, pickle: MyPickle, f: str=None, t: str=None, **kwargs):
        super().__init__(pickle)
        self.from_ = client_problems_library + f if f else client_problems_library
        self.to = server_problems_library + t if t else server_problems_library

    def execute(self):
        os.makedirs(self.to, exist_ok=True)

        send = Send(pickle=None, path=self.from_,
                    path_to_remove=client_problems_library)

        self.pickle.send(send.create_dictionary())

        try:
            self.pickle.receive_folder(save_to=self.to)
        except ValueError as e:
            return

        else:
            success_message = "Library was saved at " + self.to
            self.pickle.send(Success(success_message).create_dictionary())

            self.pickle.send(Terminate().create_dictionary())
