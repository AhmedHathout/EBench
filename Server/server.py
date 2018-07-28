#!/usr/bin/env python3
import argparse
import socket
from threading import Thread, Event

import sys
sys.path.append("../")

from lib.my_pickle import MyPickle
from Server.session.session import Session

def parse_args():
    """Parse the arguments given by stdin

    Returns:
        namespace: An object having host and port values as attributes
    """

    # Create the parser.
    parser = argparse.ArgumentParser(description="Getting the host and port to"
                                               " connect to the server")

    # Add the optoional argument 'host'.
    parser.add_argument("--host", help="The host ip address "
                                     "(default='127.0.0.1')",
                      type=str, default='127.0.0.1')

    # Add the optional argument 'port'.
    parser.add_argument("--port", help="The port number (default=1998)",
                      type=int, default=1998)

    # parse and return
    return parser.parse_args()


class Server(object):
    """The main class of the server side."""

    def __init__(self, host, port):
        """Create new Server"""

        self.host = host
        self.port = port

        # List of all the still running jobs to be accessible from any thread.
        self.running_jobs = []

        # List of all the connections.
        self.sessions = []

        # This is to avoid race conditions while assigning an ID for a job.
        self.job_id_lock = Event()
        self.job_id_lock.set()

        # This is to avoid race conditions while adding and removing jobs
        # From 'running_jobs'.
        self.running_jobs_lock = Event()
        self.running_jobs_lock.set()

    def serve_client(self, connection, address):
        """
        Serves the client by accepting requests, executing them then sending back the responses

        Args:
            Connection: The accept socket that links the server with accepted client.
            Address: The IP address of the client.
        """

        # Create it to be able to send and receive any picklable data.
        pickle = MyPickle(socket_=connection)

        client_libraries = pickle.receive()

        # Create a new session for this client.
        session = Session(pickle, address, client_libraries, self.running_jobs,
                          self.running_jobs_lock, self.job_id_lock)

        # Append it to the list of sessions. This is completely useless.
        self.sessions.append(session)

        # This to close the socket if the client disconnects.
        try:

            # Start accepting the client requests.
            session.run()
        except KeyboardInterrupt:

            # Close the socket.
            session.close()

        # Remove it from the list. Still useless
        self.sessions.remove(session)

    def main(self):
        """The main method for the server that does all the work."""

        # Create a new socket object.
        socket_ = socket.socket()

        # This is to be able to use the same port after the server disconnects.
        socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Assigns the socket to 'host' and 'port'
        socket_.bind((self.host, self.port))

        # Start listening for incoming connectinos.
        socket_.listen(5)
        print("Server is listening on port ", self.port)

        try:
            while True:
                # Wait till receiving a new connection then create a socket
                # for it ('connection').
                connection, address = socket_.accept()
                print("Connection from: " + str(address))

                # Create a new thread that runs the 'serve_client' method.
                serve_thread = Thread(name="serve", target=self.serve_client, args=(connection, address,))

                # Start the new thread.
                serve_thread.start()

        except Exception:
            socket_.close()


if __name__ == "__main__":
    # Get the args from sys.argv
    args = parse_args()

    # Create a new server with host and port.
    server = Server(args.host, args.port)

    # Move it.
    server.main()
