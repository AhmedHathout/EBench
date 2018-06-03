from server_response.response_types.status.status import Status


class Success(Status):
    def __init__(self, message: str, **kwargs):
        super().__init__(message)

    def execute(self):
        print(self.message)
