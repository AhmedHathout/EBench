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
            
            import os
            
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, path)

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