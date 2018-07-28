from lib.my_pickle import MyPickle
from Server.requests.request import Request
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class Help(Request):
    """Get all the possible instructions."""

    def __init__(self, pickle: MyPickle, **kwargs):
        """Create a new object.

        Args:
            pickle: Used to send and receive messages.
        """

        super().__init__(pickle)

    def execute(self):

        # Import the Parsers object.
        from parsers.argparser import Parsers

        # The first line of the help message.
        help_message = "Here is a list of all the instructions:-\n"

        # Create a new instance from Parsers in order to have access to its
        # dictionary.
        for key, value in Parsers(None, None, None, None).parsers.items():

            # Add every key to that dictionary.
            help_message += " -" + key + "\n"

        # The last line of the help message.
        help_message += "Select any of them and type -h to learn more about it"

        # Send the message.
        self.pickle.send(Success(help_message).create_dictionary())
        self.pickle.send(Terminate().create_dictionary())
