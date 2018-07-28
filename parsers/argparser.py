from argparse import ArgumentParser
from threading import Event

from Server.requests.request_types.help import Help
from Server.requests.request_types.listjobs import ListJobs
from Server.requests.request_types.listprobs import ListProbs
from Server.requests.request_types.listprovers import ListProvers
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
from libraries_paths.libraries_paths import server_problems_library
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate
from multiprocessing import cpu_count



class TolerantArgumentParser(ArgumentParser):
    """A modified version of the ArgumentParser class.

    It has one more attribute than its parent class. It is the class assigned
    to that request."""

    def __init__(self, RequestType: type, *args, **kwargs):
        """Create a new object.

        Args:
            *args, **kwargs: The same arguments that its parent class has.
            RequestType: A type object that can be used to initialize an object
                         from a subclass of request class.
            """
        super().__init__(*args, **kwargs)
        self.RequestType = RequestType

    def error(self, message):
        """A modified version of the ArgumentParser.error()

        This is to prevent the parser from printing the error on the server.
        Instead it raises an error that is handled in Parsers.execute()
        """

        help_message = self.format_help()
        error_message = '%s: error: %s\n' % (self.prog, message)
        message = help_message + error_message
        raise ValueError(message)

    def print_help(self, file=None):
        """A modified version of the ArgumentParser.print_help()

        This is to prevent the parser from printing the help message on the
        server's stderr. Instead it raises an error that is handled in
        Parsers.execute()
        """

        raise ValueError(self.format_help())

    def execute(self, argv: [], pickle: MyPickle, client_libraries,
                running_jobs: [Job], running_jobs_lock: Event,
                job_id_lock: Event):

        """Create an object from a subclass of the request class

        Args:
            argv: The arguments to the instruction of the request string.
            pickle: The socket object to send and receive messages.
            running_jobs: A list of all the running jobs on the server,
            running_jobs_lock: The lock to that list.
            job_id_lock: the lock to the job ID generator.
        """

        # Call the native parse_args method and convert the result to a dict.
        args = self.parse_args(argv).__dict__

        # Update the dictionary of the arguments.
        args.update({"pickle" : pickle,
                     "client_libraries": client_libraries,
                     "running_jobs": running_jobs,
                     "running_jobs_lock": running_jobs_lock,
                     "job_id_lock": job_id_lock})

        # Create an object from that request by passing the dictionary args.
        request = self.RequestType(**args)

        # Execute the request.
        request.execute()


class Parsers(object):
    def __init__(self, pickle:MyPickle, client_libraries: {str, str},
                 running_jobs: [Job], running_jobs_lock: Event, job_id_lock: Event):
        """Initialize an object from parsers.

        Args:
            argv: The arguments to the instruction of the request string.
            pickle: The socket object to send and receive messages.
            running_jobs: A list of all the running jobs on the server,
            running_jobs_lock: The lock to that list.
            job_id_lock: the lock to the job ID generator.
        """

        # get a dictionary containing all the parsers.
        self.parsers = self.initialize_parsers()
        self.pickle = pickle
        self.client_libraries = client_libraries
        self.running_jobs = running_jobs
        self.running_jobs_lock = running_jobs_lock
        self.job_id_lock = job_id_lock

    def initialize_parsers(self):
        """Initialize all the parsers.

        This method creates a TolerantArgumentParser for every request type
        """

        # Parser for createlib instruction. The request type is the class
        # associated with that instruction.

        createlib_parser = TolerantArgumentParser(description="arguments for the createlib instruction", RequestType=CreateLib)

        # Add the arguments to the parser.
        createlib_parser.add_argument("directory", help="Specify the "
                                                          "directories that "
                                                          "should be created "
                                                          "starting from the "
                                                          "problem_library "
                                                          "folder on the "
                                                          "Server", )

        addprobs_parser = TolerantArgumentParser(description="arguments for the addprobs instruction", RequestType=AddProbs)
        addprobs_parser.add_argument("-f",
                                     help="Specifies the probelm directory "
                                          "on the client (default: everthing"
                                          "in problems_to_submit")

        addprobs_parser.add_argument("-t",
                                     help="Specifies where the problems should "
                                          "be saved after the problems_library "
                                          "folder on the Server "
                                          "(default: main folder")

        subjob_parser = TolerantArgumentParser(description="arguments for the "
                                                            "subjob "
                                                            "instruction", RequestType=SubJob)
        subjob_parser.add_argument("-po", "--prover-options",
                                   default="--auto -s --print-statistics "
                                             "--print-version",
                                   help="The options for the prover "
                                        "(default: %(default)s)")

        subjob_parser.add_argument("-pp", "--maximum_problems_in_parallel",
                                   default=cpu_count(),
                                   help="Number of problems that can run in " \
                                        "parallel (default: %(default)d)",
                                   type=int)

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

        listprovers_parser = TolerantArgumentParser(description="Lists all the "
                                                            "provers",
                                                 RequestType=ListProvers)

        listprobs_parser = TolerantArgumentParser(description="Lists all the "
                                                              "problems "
                                                              "libraries",
                                                 RequestType=ListProbs)

        listprobs_parser.add_argument("-r", "--recursive",
                                      action="store_true",
                                      help="If specified, the sublibraries "
                                           "will also be printed")

        listprobs_parser.add_argument("-d", "--directory",
                                      help="directory to start with "
                                           "(default: %(default)s))",
                                      default=server_problems_library)

        help = TolerantArgumentParser(description="Displays all instructions",
                                      RequestType=Help)

        # A dictionary containing all of these parsers. The key is the class
        # name in lower case and the value is the paresr itself.
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
                   ListProvers.__name__.lower(): listprovers_parser,
                   ListProbs.__name__.lower(): listprobs_parser,
                   "help": help}

        return parsers

    def execute(self, string_request: str):
        """Creates the associated parser and passes the request to it.

        Args:
            string_request: The client request.
        """

        # Check if the request is an empty string.
        if not string_request:
            # Tell the client to prompt the user to enter another command.
            self.pickle.send(Terminate().create_dictionary())
            return

        # Split the request. shlex was used here in order not to split quoted
        # strings.
        split = shlex.split(string_request, posix=False)

        # The instruction is the first word in the request.
        instruction = split[0].strip()

        # The arguments to that instruction is the rest of the request.
        argv = split[1:]

        # Try to execute the request. Get the right parser by the instruction
        try:
            self.parsers[instruction].execute(argv=argv, pickle=self.pickle,

                                              client_libraries=
                                              self.client_libraries,

                                              running_jobs=self.running_jobs,

                                              job_id_lock=self.job_id_lock,

                                              running_jobs_lock=
                                              self.running_jobs_lock)
        except KeyError as e:
            # A KeyError was raised because the instruction does not exist
            # (Not in the parsers dictionary). Create an error and send it
            # to the client.
            error = Error("No such instruction: " + str(e))
            self.pickle.send(error.create_dictionary())


        except ValueError as e:
            # This is raised because of the help or error message.
            self.pickle.send(Success(str(e)).create_dictionary())
            self.pickle.send(Terminate().create_dictionary())
