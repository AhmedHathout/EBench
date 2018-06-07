import os

from libraries_paths.libraries_functions import *


class Configuration(object):

    def __init__(self, prover_options: str, prover_id: str):
        self.prover_options = prover_options.replace("'", "")
        self.prover_id = prover_id

    def verify_prover(self):
        if not os.path.isdir(get_prover_path(self.prover_id)):
            raise OSError("No prover with such id: " + self.prover_id)