from server_response.response import Response


class Terminate(Response):

    def __init__(self, **kwargs):
        pass

    def execute(self):
        raise NotImplementedError
