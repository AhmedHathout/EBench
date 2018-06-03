import sys

from server_response.response_types.status.status import Status
from server_response.response_types.terminate import Terminate


class Error(Status):

    def __init__(self, message: str, **kwargs):
        super().__init__(message)

    def execute(self):
        sys.stderr.write(self.message + "\n")
        Terminate().execute()
