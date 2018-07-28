import json

import os

from lib.my_pickle import MyPickle
from Server.job.job import Job
from Server.requests.request import Request
from libraries_paths.libraries_paths import provers_library
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class ListProvers(Request):
    """List all the submitted provers."""

    def __init__(self, pickle:MyPickle, **kwargs):
        """Create an object.

        Args:
            pickle: Used to send and receive messages.
        """
        super().__init__(pickle)

    def execute(self):

        # List the directory that has all the provers. Remove the first letter
        # as the server adds 'E' at the beginning of every ID. Sort them.
        provers = sorted([prover[1:] for prover in os.listdir(provers_library)])

        # Check if there are no provers.
        if not provers:
            message = "No provers found!"
        else:
            # Create a success instance having its message as the list of the
            # provers.
            message = "Here is a list of the ids of the provers:-\n" + \
                "\n".join(provers)

        success = Success(message)
        self.pickle.send(success.create_dictionary())
        self.pickle.send(Terminate().create_dictionary())