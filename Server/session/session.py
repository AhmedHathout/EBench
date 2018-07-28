from threading import Event
from lib.my_pickle import MyPickle
from parsers.argparser import Parsers
from Server.job.job import Job
from server_response.response_types.status.status_types.error import Error


class Session(object):
    """Receive the request from the client and pass it parsers to be handled."""

    def __init__(self, pickle: MyPickle, address: str,
                 client_libraries: {str, str}, running_jobs: [Job],
                 running_jobs_lock: Event, job_id_lock: Event):
        """Create a new object

        Args:
            pickle: The socket used to receive requests and send responses.
            address: The IP address of the client.
            running_jobs: A list of all the running jobs on the server.
            running_jobs_lock: An event to indicate if it is possible to make
                               changes to the running_jobs list.
            job_id_lock: An event to indicate if it is possible to generate a
                         new ID for the job.
            """
        self.pickle = pickle
        self.address = address
        self.client_libraries = client_libraries

        # Create a new parsers object that will be used to parse and execute
        # The request.
        self.parsers = Parsers(self.pickle, client_libraries, running_jobs,
                               running_jobs_lock, job_id_lock)

    def execute(self, request: str):
        """Call execute on parsers to execute the request.

        Args:
            request: The string request the client sent.
        """
        self.parsers.execute(request)

    def run(self):
        """Keep receiving requests and passing them to the parsers."""

        while True:
            # Receive request.
            request = self.pickle.receive()

            # Try to execute it.
            try:
                self.execute(request)

            # If there is an error that was not handled in any other module,
            # send it to the client that will print it to the user.
            # It is very unlikely that this occurs.
            except ValueError as e:
                self.pickle.send(Error(str(e)).create_dictionary())
                return

    def close(self):
        """Close connection."""
        self.pickle.socket_.close()