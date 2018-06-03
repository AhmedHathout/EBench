from abc import ABC, abstractmethod
from server_response.response_parser import ResponseParser


class Response(ABC):

    @abstractmethod
    def execute(self):
        pass

    def create_dictionary(self) -> {str: object}:
        dictionary = {ResponseParser.class_: self.__class__.__name__,
                      ResponseParser.args: self.__dict__}

        return dictionary
