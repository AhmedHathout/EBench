from threading import Event
from lib.my_pickle import MyPickle
from parsers.argparser import Parsers
from Server.job.job import Job
from server_response.response_types.status.status_types.error import Error


class Session(object):

    def __init__(self, pickle: MyPickle, address: str,
                 running_jobs: [Job], running_jobs_lock: Event, job_id_lock: Event):

        self.pickle = pickle
        self.address = address
        self.client_requests = []
        self.parsers = Parsers(self.pickle, running_jobs, running_jobs_lock,
                               job_id_lock)

    def execute(self, request: str):
        self.parsers.execute(request)

    def run(self):
        while True:
            request = self.pickle.receive()

            try:
                self.execute(request)
            except ValueError as e:
                self.pickle.send(Error(str(e)).create_dictionary())
                return
