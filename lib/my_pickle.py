import os
import pickle
from socket import socket
from time import sleep

from lib.directory import directorize, remove_file_name


class MyPickle(object):
    def __init__(self, socket_: socket):
        self.socket_ = socket_

    def send(self, data) -> None:
        data_pickle = pickle.dumps(data)
        self.socket_.send(data_pickle + "end".encode('utf-8').strip())
        sleep(.1)

    def receive(self):
        chunk = 64 * 1024
        data_pickle = b''
        data_chunck = self.socket_.recv(chunk)
        while True:
            data_pickle += data_chunck
            if data_chunck.endswith("end".encode()):
                break
            data_chunck = self.socket_.recv(chunk)

        data = pickle.loads(data_pickle)
        return data

    def send_folder(self, folder: str, path_to_remove: str) -> [(str, str)]:
        def __get_all_folder_contents(folder: str, data:[(str, str)]=[]):

            if os.path.isfile(folder):
                with open(folder, "r") as f:
                    file_ = f.read()
                data.append((folder.replace(path_to_remove, ""), file_))

            else:
                folder = directorize(folder, remove_slash=False)

                if os.path.isdir(folder):
                    for item in os.listdir(folder):
                        __get_all_folder_contents(folder + item, data)

            return data

        contents = __get_all_folder_contents(folder)
        self.send(contents)
        if not contents:
            raise ValueError("No data to send")

    def receive_folder(self, save_to: str) -> None:
        data = self.receive()

        if not data:
            raise ValueError("No data was sent")

        for file_path, file_data in data:
            full_path = save_to + file_path
            os.makedirs(remove_file_name(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(file_data)

    def connect(self, args):
        self.socket_.connect(args)