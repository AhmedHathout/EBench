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
    """List the folders in problems_library."""

    def __init__(self, pickle:MyPickle, directory: str, recursive: bool,
                 **kwargs):

        """create a new object.

        Args:
            directory: The folder to list its contents.
            recursive: List subfolders.
        """
        super().__init__(pickle)
        self.directory = directory
        self.recursive = recursive

    def execute(self):

        if self.recursive:
            libraries = []

            # Get a list of tuples: [(root path, folders in it, files in it).
            # Loop on it and append the folders only to the list that will be
            # sent to the client.
            for root, folders, files_ in os.walk(self.directory):
                for folder in folders:
                    libraries.append(os.path.join(root, folder))

        else:

            # Get the contents of this folder including files.
            libraries = os.listdir(server_problems_library)

        if libraries:
            # Found some folders in the library
            message = "Here is a list of the libraries:-\n- " + \
                      "\n- ".join(libraries)

        else:
            # Nothing was found. Send some text instead of empty list.
            message = "No libraries found!"

        # Create and send the success message.
        success = Success(message)
        self.pickle.send(success.create_dictionary())
        self.pickle.send(Terminate().create_dictionary())
