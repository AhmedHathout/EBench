"""
    This module is a wrapper for the MyPickle class.
"""

import os
import pickle
from socket import socket
from time import sleep

from lib.directory import directorize, remove_file_name


class MyPickle(object):
    """Add more features to the socket object.

    send() -- send any picklable object
    receive() -- receive any picklable object
    send_folder() -- send a file or folder with its contents
    receive_folder() -- receive that file or folder :-)
    connect() -- call connect() on the socket object
    """
    def __init__(self, socket_: socket):
        """Create a new object

        Args:
            socket: Well, it is the socket connecting it to the other side.
            """
        self.socket_ = socket_

    def send(self, data) -> None:
        """Send any picklable object

        Args:
            data: The object that is to be sent.
        """

        # Serialize data
        data_pickle = pickle.dumps(data)

        # Append the encoded string "end" indicating end of data
        self.socket_.send(data_pickle + "end".encode('utf-8').strip())

        # This delay is to make sure that messages that should be printed
        # on stderr will not be printed at the same time with message that
        # should be printed on stdout
        sleep(.1)

    def receive(self):
        """Receive the data that was sent by send()

        Returns:
            object: the data it received of course :-)
        """

        # How many bytes should be received in every iteration.
        # It can be any other value.
        chunk = 64 * 1024

        # Initializing the byte stream.
        data_pickle = b''

        # Receiving the first chunk of data.
        data_chunk = self.socket_.recv(chunk)

        # This is mainly for the server. It is to make sure that the server
        # will stop waiting for data if the client disconnects.
        if not data_chunk:
            # This exception was used cause the client most of the time
            # raises a keyboard interrupt when it disconnects.
            raise KeyboardInterrupt

        # Receive the rest of chunks.
        while True:
            data_pickle += data_chunk

            # Check if this is the end of data.
            if data_pickle.endswith("end".encode()):
                break

            # -No
            # -Receive the next chunk then.
            data_chunk = self.socket_.recv(chunk)

        # Unpickle the data. Convert it to its original data type.
        data = pickle.loads(data_pickle)

        # And of course return it.
        return data

    def send_folder(self, folder: str, path_to_remove: str) -> [(str, str)]:
        """Send a folder and its contents.

        Args:
            folder: Path to folder.
            path_to_remove: The prefix that should be removed from the path.
        """

        def __get_all_folder_contents(path: str, data:[(str, str)]):
            """
            Read all files in the given path 'path' and its subfolders
            Provided that it is a folder.

            Args:
                path: Path to folder or file.
                data: A list of tuples. The second entry of a tuple is the
                      file and the first is the path to it. These files
                      are the read files.

            Returns:
                [(str, str)]: It is the very same argument 'data' (It is a
                              recursive function).
            """

            # Check if 'path' is a file.
            if os.path.isfile(path):
                # -It is a file
                # -Good, no need for more recursion then. read it.
                with open(path, "rb") as f:
                    file_ = f.read()

                # now add it to our list 'data'.
                data.append((path.replace(path_to_remove, ""), file_))

            else:
                # -No it is a folder.
                # -Then we will have to do the same for all of its contents.
                # First ensure that it ends with a '/' as we will append
                # another string to it.
                path = directorize(path)

                # Useless if condition. Or at least I do not remember why it
                # is here. If it is not a file then it is a directory.
                if os.path.isdir(path):

                    # Loop on every item in that folder.
                    for item in os.listdir(path):
                        # Now repeat the process but for this item instead.
                        __get_all_folder_contents(path + item, data)

            return data

        # Read everythin in that folder.
        # Before we start, the list is empty as no file was read.
        contents = __get_all_folder_contents(folder, [])

        # Send the contents. It is a list of tuples so it can be pickled.
        self.send(contents)

        # Nothing was in that folder or does not exist!
        # Raise an error then, let every side handle that error itself.
        if not contents:
            raise ValueError("No data to send")


    def receive_folder(self, save_to: str) -> None:
        """Receives the folder that was sent by send_folder()

        Args:
            save_to: Where to save this damn folder to.
        """

        # Make sure that it ends with '/'
        save_to = directorize(save_to)
        data = self.receive()

        # Raise an error if there is no data. Let each side de-side what to
        # do in this situation.
        if not data:
            raise ValueError("No data was sent")

        # Loop on the received data.
        for file_path, file_data in data:

            # Append to 'save_to' since its the main folder.
            # The received file may need to be saved in a subfolder
            full_path = save_to + file_path

            # Make this subfolder. If it exists then do not raise an error.
            os.makedirs(remove_file_name(full_path), exist_ok=True)

            # Write that file in that folder.
            with open(full_path, "wb") as f:
                f.write(file_data)

    def connect(self, args):
        """Says heeello tooo theeee other siiide.

        Args:
            The host and port for the socket object as a tuple.
        """
        self.socket_.connect(args)