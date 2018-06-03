from server_response.response import Response


class Status(Response):
    def __init__(self, message: str):
        self.message = message
