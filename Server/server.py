import socket
from threading import Thread, Event

from lib.my_pickle import MyPickle
from Server.session.session import Session


class Server(object):
    def __init__(self, host="127.0.0.1", port=1997):
        self.host = host
        self.port = port
        self.running_jobs = []
        self.sessions = []
        self.job_id_lock = Event()
        self.job_id_lock.set()
        self.running_jobs_lock = Event()
        self.running_jobs_lock.set()

    def serve_client(self, connection, address):
        pickle = MyPickle(socket_=connection)
        session = Session(pickle, address, self.running_jobs,
                          self.running_jobs_lock, self.job_id_lock)

        self.sessions.append(session)
        session.run()
        self.sessions.remove(session)

    def main(self):

        socket_ = socket.socket()
        socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_.bind((self.host, self.port))

        socket_.listen(5)
        print("Server is listening on port ", self.port)

        try:
            while True:
                connection, address = socket_.accept()
                print("Connection from: " + str(address))

                serve_thread = Thread(name="serve", target=self.serve_client, args=(connection, address,))
                serve_thread.start()

        except Exception:
            socket_.close()


if __name__ == "__main__":
    server = Server()
    server.main()
