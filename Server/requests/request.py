from abc import ABC, abstractmethod
from lib.my_pickle import MyPickle


class Request(ABC):
    """An abstract class for all the request types"""

    def __init__(self, pickle: MyPickle):
        self.pickle = pickle

    @abstractmethod
    def execute(self):
        """How the request type should behave."""
        pass
