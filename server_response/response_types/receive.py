from lib.my_pickle import MyPickle
from server_response.response import Response


class Receive(Response):

    def __init__(self, pickle: MyPickle, path: str, **kwargs):
        self.pickle = pickle
        self.path = path

    def execute(self):
        print("Receiving {} ...".format(self.path))
        self.pickle.receive_folder(save_to=self.path)

