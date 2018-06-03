from lib.my_pickle import MyPickle
from Server.requests.request import Request
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class Help(Request):

    def __init__(self, pickle: MyPickle, **kwargs):
        super().__init__(pickle)

    def execute(self):
        from parsers.argparser import Parsers
        help_message = "Here is a list of all the instructions:-\n"
        for key, value in Parsers(None, None, None, None).parsers.items():
            help_message += " -" + key + "\n"

        help_message += "Select any of them and type -h to learn more about it"

        self.pickle.send(Success(help_message).create_dictionary())
        self.pickle.send(Terminate().create_dictionary())
