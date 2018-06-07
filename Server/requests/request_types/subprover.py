import os

from lib.directory import remove_file_name
from lib.my_pickle import MyPickle
from Server.install_prover.install_prover import Installer
from Server.requests.request import Request
from server_response.response_types.send import Send
from libraries_paths.libraries_functions import *
from server_response.response_types.status.status_types.error import Error
from server_response.response_types.status.status_types.success import Success
from server_response.response_types.terminate import Terminate


class SubProver(Request):

    def __init__(self, pickle: MyPickle, path: str, prover_id: str, **kwargs):

        super().__init__(pickle)
        self.path = path
        self.prover_id = prover_id

    def execute(self):
        path_to_remove = remove_file_name(self.path)

        if not self.path.endswith("/E.tgz"):
            error = Error("The file must be named E.tgz and should contain the"
                          "folder E/")
            self.pickle.send(error.create_dictionary())
            return

        send = Send(None, self.path, path_to_remove)

        self.pickle.send(send.create_dictionary())
        prover_path = get_prover_path(self.prover_id)
        os.makedirs(prover_path, exist_ok=True)

        self.pickle.receive_folder(save_to=prover_path)

        success = Success("Extracting and installing...")
        self.pickle.send(success.create_dictionary())

        installer = Installer(self.prover_id)
        try:
            installer.install()

        except OSError as e:
            self.pickle.send(Error(str(e)).create_dictionary())

        else:
            success = Success("Prover submitted and installer")
            self.pickle.send(success.create_dictionary())
            self.pickle.send(Terminate())
