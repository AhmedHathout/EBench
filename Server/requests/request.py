from abc import ABC, abstractmethod
from lib.my_pickle import MyPickle


class Request(ABC):

    def __init__(self, pickle: MyPickle):
        self.pickle = pickle

    @abstractmethod
    def execute(self):
        pass
