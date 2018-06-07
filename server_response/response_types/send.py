from lib.my_pickle import MyPickle
from server_response.response import Response


class Send(Response):

    def __init__(self, pickle: MyPickle, path: str, path_to_remove, **kwargs):
        self.pickle = pickle
        self.path = path
        self.path_to_remove = path_to_remove

    def execute(self):
        print("Sending {} ...".format(self.path))
        self.pickle.send_folder(self.path, self.path_to_remove)