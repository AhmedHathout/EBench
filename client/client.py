import sys
from socket import socket
from time import sleep

from lib.my_pickle import MyPickle
from server_response.response_parser import ResponseParser


class Client(object):
    def __init__(self):
        socket_ = socket()
        self.pickle = MyPickle(socket_)
        self.response_parser = ResponseParser(self.pickle)

    def initiate_connection(self, host: str, port: int):
        self.pickle.connect((host, port))

    def run(self):
        while(True):
            sleep(0.1)
            request = input("-> ")
            self.pickle.send(request)
            self.handle_response()

    def handle_response(self):
        try:
            while(True):
                server_response = self.pickle.receive()
                self.response_parser.execute(server_response)

        except NotImplementedError:
            pass

        except ValueError as e:
            sys.stderr.write(str(e) + "\n")

if __name__ == '__main__':
    client = Client()
    # host = input("Please enter the host")
    # port = int(input("Please enter the port"))
    host = '127.0.0.1'
    port = 1997
    client.initiate_connection(host, port)
    client.run()



