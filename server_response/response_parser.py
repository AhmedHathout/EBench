from socket import socket

from lib.my_pickle import MyPickle


class ResponseParser(object):

    class_ = "class"
    args = "args"

    def __init__(self, pickle:MyPickle):
        self.pickle = pickle

    def execute(self, response: {str: str}):

        from server_response.response_types.send import Send
        from server_response.response_types.status.receive import Receive
        from server_response.response_types.status.status_types.error import Error
        from server_response.response_types.status.status_types.success import Success
        from server_response.response_types.terminate import Terminate

        parser = {Send.__name__: Send,
                  Receive.__name__: Receive,
                  Terminate.__name__: Terminate,
                  Success.__name__: Success,
                  Error.__name__: Error}

        class_name = response[ResponseParser.class_]
        args = self.update_args(response)
        parser[class_name](**args).execute()

    def update_args(self, response: dict):
        response[ResponseParser.args].update({"pickle": self.pickle})
        return response[ResponseParser.args]
