#!/usr/bin/env python3

import os
from argparse import ArgumentParser
from lib.directory import directorize

def prepare_input_path(path: str) -> str:
    return directorize(os.path.abspath(os.path.expanduser(
        path)), remove_slash=False)

if __name__ == '__main__':
    argparser = ArgumentParser(description="For parsing paths")
    argparser.add_argument("-s","--server-library",
                           help="The main library path that will contain all the "
                                "other libraries for the Server")

    argparser.add_argument("-c","--client-library",
                           help="The main library path that will contain all the "
                                "other libraries for the client")

    args = argparser.parse_args()

    default_server_library = directorize(os.path.abspath("./server_libraries/"))
    default_client_library = directorize(os.path.abspath("./client_libraries/"))

    server_libraries = prepare_input_path(args.server_library) if \
        args.server_library else default_server_library

    client_libraries = prepare_input_path(args.client_library) if \
        args.client_library else default_client_library

    jobs = "jobs/"
    jobs_reports = jobs + "reports/"
    jobs_results = jobs + "results/"

    libraries = {"provers_library": server_libraries + "provers_library/",
                 "server_problems_library": server_libraries +
                                            "problems_library/",
                 "server_jobs_reports_library": server_libraries +
                                                jobs_reports,
                 "server_jobs_results_library": server_libraries +
                                                jobs_results,
                 "client_problems_library": client_libraries +
                                          "problems_to_submit/",
                 "client_jobs_reports_library": client_libraries +
                                                jobs_reports,
                 "client_jobs_results_library": client_libraries +
                                                jobs_results,
                 "jobs_ids": client_libraries + jobs +
                             "IDs_of_submitted_jobs/"
                 }


    with open("libraries_paths/libraries_paths.py", "w") as f:
        for key, value in libraries.items():
            f.write(key + " = \"" + value + "\"")
            f.write("\n")
            os.makedirs(value, exist_ok=True)

