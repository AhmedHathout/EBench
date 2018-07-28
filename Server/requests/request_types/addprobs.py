import os
from lib.my_pickle import MyPickle
from Server.requests.request import Request
from server_response.response_types.send import Send
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate
from libraries_paths.libraries_paths import *


class AddProbs(Request):
    """Send a folder containing problem files from the client to the server."""

    def __init__(self, pickle: MyPickle, f: str=None, t: str=None, **kwargs):
        """Create a new object.

        Args:
            pickle: Used to send and receive messages.
            f: The folder to be sent from the client.
            t: The path in which the sent folder should be saved on the server.
        """
        super().__init__(pickle)
        self.from_ = f
        self.to = server_problems_library + t if t \
            else server_problems_library

    def execute(self):
        # Make the directories needed to save the incoming folder/
        os.makedirs(self.to, exist_ok=True)

        # Ask the client to send the folder.
        # pickle is None here since if it were sent, the client would not be
        # able to use it because the receiver would be the client it self not
        # the server. The client would update it itself.
        send = Send(pickle=None, path=self.from_,
                    path_to_remove=os.path.dirname(self.from_))

        # Send send to the client after converting it to a dictionary.
        self.pickle.send(send.create_dictionary())

        # Try to receive the folder.
        try:
            self.pickle.receive_folder(save_to=self.to)
        except ValueError as e:
            # No data was sent. exit and wait for the next request.
            return

        else:

            # Data was sent and saved. Inform the client.
            success_message = "Library was saved at " + self.to
            self.pickle.send(Success(success_message).create_dictionary())

            self.pickle.send(Terminate().create_dictionary())
