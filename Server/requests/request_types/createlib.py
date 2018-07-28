import os

from lib.my_pickle import MyPickle
from libraries_paths.libraries_paths import server_problems_library
from Server.requests.request import Request
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class CreateLib(Request):
    """A Request subclass for executing createlib requests."""

    def __init__(self, pickle: MyPickle, directory: str, **kwargs):
        """Create a new object.

        Args:
            pickle: Used to send and receive messages.
            directory; The directory of the library to be created.
        """

        # Call the constructor of the super class.
        super().__init__(pickle)
        self.directory = directory

    def execute(self):
        """Execute the request."""

        # Try to make the directory the client asked for.
        try:
            os.makedirs(server_problems_library + self.directory)

        except OSError as e:
            # - That directory already exists.
            # - Then send that to the client.
            self.pickle.send(Error(str(e)).create_dictionary())

        else:

            # Inform the client that the library was created.
            # 1. Define the success message.
            success_message = "Library " + self.directory + \
                              " was created successfully"

            # 2. Create the success object using this message.
            success = Success(success_message)

            # 3. Create a dictionary of it.
            success_dictionary = success.create_dictionary()

            # 4. Send that dictionary to the client.
            self.pickle.send(success_dictionary)

            # Send Terminate to the client so that it prompts the user to enter
            # the next command
            # 1. Create an instance from Terminate.
            terminate = Terminate()

            # 2. Create a dictionary from it.
            terminate_dictionary = terminate.create_dictionary()

            # 3. send that dictionary.
            self.pickle.send(terminate_dictionary)
