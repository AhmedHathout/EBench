#!/usr/bin/env python3
import argparse
import sys
sys.path.append("../")

from socket import socket
from time import sleep

from lib.my_pickle import MyPickle
from server_response.response_parser import ResponseParser


def parse_args():
    args = argparse.ArgumentParser(description="Getting the host and port to"
                                               " connect to the server")

    args.add_argument("--host", help="The host ip address "
                                     "(default: %(default)s)",
                      type=str, default='127.0.0.1')

    args.add_argument("--port", help="The port number (default: %(default)d)",
                      type=int, default=1998)

    return args.parse_args()

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
    args = parse_args()

    client = Client()
    client.initiate_connection(args.host, args.port)
    try:
        client.run()
    except KeyboardInterrupt:
        pass



