import subprocess
import tarfile
from libraries_paths.libraries_functions import *

class Installer(object):

    def __init__(self, prover_id):
        self.prover_id = prover_id

    def extract_prover(self):
        path = get_prover_path(self.prover_id)
        prover_tgz = path + "E.tgz"
        with tarfile.open(prover_tgz) as tar:
            tar.extractall(path)

    def configure(self):
        path_to_configure_file = get_prover_path(self.prover_id) + "E/"
        commands = ["./configure --bindir=" + get_prover_bin(self.prover_id),
                    "make",
                    "make install"]

        for command in commands:
            data, error = subprocess.Popen(command, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, shell=True,
                                           cwd=path_to_configure_file,
                                           universal_newlines=True).communicate()

            if error:
                raise OSError(error)

    def install(self):
        self.extract_prover()
        self.configure()