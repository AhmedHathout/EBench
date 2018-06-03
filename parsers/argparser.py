from argparse import ArgumentParser
from threading import Event

from Server.requests.request_types.help import Help
from Server.requests.request_types.listjobs import ListJobs
from lib.my_pickle import MyPickle
import shlex

from Server.job.job import Job
from Server.requests.request_types.addprobs import AddProbs
from Server.requests.request_types.createlib import CreateLib
from Server.requests.request_types.jobreport import JobReport
from Server.requests.request_types.jobresults import JobResults
from Server.requests.request_types.jobstatus import JobStatus
from Server.requests.request_types.killjob import KillJob
from Server.requests.request_types.rerun import Rerun
from Server.requests.request_types.subjob import SubJob
from Server.requests.request_types.subprover import SubProver
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class TolerantArgumentParser(ArgumentParser):

    def __init__(self, RequestType: type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RequestType = RequestType

    def error(self, message):
        help_message = self.format_help()
        error_message = '%s: error: %s\n' % (self.prog, message)
        message = help_message + error_message
        raise ValueError(message)

    def print_help(self, file=None):
        raise ValueError(self.format_help())

    def execute(self, argv: [], pickle: MyPickle, running_jobs: [Job],
                running_jobs_lock: Event, job_id_lock: Event):

        args = self.parse_args(argv).__dict__
        args.update({"pickle" : pickle,
                     "running_jobs": running_jobs,
                     "running_jobs_lock": running_jobs_lock,
                     "job_id_lock": job_id_lock})
        request = self.RequestType(**args)
        request.execute()


class Parsers(object):
    def __init__(self, pickle:MyPickle, running_jobs: [Job], running_jobs_lock: Event, job_id_lock: Event):
        self.parsers = self.initialize_parsers()
        self.pickle = pickle
        self.running_jobs = running_jobs
        self.running_jobs_lock = running_jobs_lock
        self.job_id_lock = job_id_lock

    def initialize_parsers(self):
        createlib_parser = TolerantArgumentParser(description="arguments for the createlib instruction", RequestType=CreateLib)
        createlib_parser.add_argument("directory", help="Specify the "
                                                          "directories that "
                                                          "should be created "
                                                          "starting from the "
                                                          "problem_library "
                                                          "folder on the "
                                                          "Server", )

        addprobs_parser = TolerantArgumentParser(description="arguments for the addprobs instruction", RequestType=AddProbs)
        addprobs_parser.add_argument("-f", help="Specifies the "
                                                          "probelm directory "
                                                          "on the client")

        addprobs_parser.add_argument("-t", help="Specifies where the "
                                                        "problems should be "
                                                        "saved after the "
                                                        "problems_library "
                                                        "folder on the "
                                                        "Server")

        subjob_parser = TolerantArgumentParser(description="arguments for the "
                                                            "subjob "
                                                            "instruction", RequestType=SubJob)
        subjob_parser.add_argument("-po", "--prover-options", help="The "
                                                                 "options for the prover",
                                     default="--auto -s --print-statistics "
                                             "--print-version")

        subjob_parser.add_argument("-pp", "--maximum_problems_in_parallel", help="Number "
                                                                     "of "
                                                                     "problems that can run in parallel", type=int)

        subjob_parser.add_argument("prover_id", help="The id of the prover that will run the job")

        subjob_parser.add_argument("problems_path", help="The path that "
                                                         "contains the "
                                                         "problems of the "
                                                         "job")

        jobstatus_parser = TolerantArgumentParser(description="arguments for "
                                                               "the jobstatus instruction", RequestType=JobStatus)
        jobstatus_parser.add_argument("job_id", help="The id of the required "
                                                     "job", type=int)

        jobreport_parser = TolerantArgumentParser(description="arguments for "
                                                               "the jobreport "
                                                               "instruction", RequestType=JobReport)
        jobreport_parser.add_argument("job_id", help="The id of the required "
                                                     "job", type=int)

        jobresults_parser = TolerantArgumentParser(description="arguments for "
                                                               "the jobresults "
                                                               "instruction", RequestType=JobResults)
        jobresults_parser.add_argument("job_id", help="The id of the required "
                                                     "job", type=int)

        killjob_parser = TolerantArgumentParser(description="arguments for "
                                                               "the killjob "
                                                             "instruction", RequestType=KillJob)
        killjob_parser.add_argument("job_id", help="The id of the required "
                                                     "job", type=int)

        rerun_parser = TolerantArgumentParser(description="arguments for "
                                                               "the rerun "
                                                           "instruction", RequestType=Rerun)
        rerun_parser.add_argument("job_id", help="The id of the required "
                                                     "job", type=int)

        rerun_parser.add_argument("-pp", "--maximum_problems_in_parallel", help="Number "
                                                                    "of "
                                                                    "problems that can run in parallel", type=int)

        subprover_parser = TolerantArgumentParser(description="arguments for the "
                                                              "subprover "
                                                              "instruction",
                                                  RequestType=SubProver)

        subprover_parser.add_argument("prover_id", help="The id for the prover")
        subprover_parser.add_argument("path", help="path/to/E.tgz")

        listjobs_parser = TolerantArgumentParser(description="Lists all the "
                                                            "running jobs",
                                                 RequestType=ListJobs)

        help = TolerantArgumentParser(description="Displays all instructions",
                                      RequestType=Help)

        parsers = {CreateLib.__name__.lower(): createlib_parser,
                   AddProbs.__name__.lower(): addprobs_parser,
                   SubJob.__name__.lower(): subjob_parser,
                   JobStatus.__name__.lower(): jobstatus_parser,
                   JobReport.__name__.lower(): jobreport_parser,
                   JobResults.__name__.lower(): jobresults_parser,
                   KillJob.__name__.lower(): killjob_parser,
                   Rerun.__name__.lower(): rerun_parser,
                   SubProver.__name__.lower(): subprover_parser,
                   ListJobs.__name__.lower(): listjobs_parser,
                   "help": help}

        return parsers

    def execute(self, string_request: str):
        split = shlex.split(string_request, posix=False)
        instruction = split[0].strip()
        argv = split[1:]
        try:
            self.parsers[instruction].execute(argv=argv, pickle=self.pickle,
                                              running_jobs=self.running_jobs,
                                              job_id_lock=self.job_id_lock,
                                              running_jobs_lock=
                                              self.running_jobs_lock)
        except KeyError as e:
            error = Error("No such instruction: " + str(e))
            self.pickle.send(error.create_dictionary())

        except ValueError as e:
            self.pickle.send(Success(str(e)).create_dictionary())
            self.pickle.send(Terminate().create_dictionary())
