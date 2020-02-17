import select
import socket

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'


class EpollServerSocket:
    def __init__(self, host, port):
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sckt.bind((host, port))
        self.sckt.listen(1)
        self.sckt.setblocking(False)

        self.epoll = select.epoll()
        self.epoll.register(self.sckt.fileno(), select.EPOLLIN)

        self.connections = {}
        self.requests = {}
        self.responses = {}

    @property
    def events(self):
        return self.epoll.poll(1)

    def register_connection(self):
        connection, _ = self.sckt.accept()
        connection.setblocking(False)

        self.epoll.register(connection.fileno(), select.EPOLLIN)

        self.connections[connection.fileno()] = connection
        self.requests[connection.fileno()] = b''

    def read_from_connection(self, file_no, callback):
        self.requests[file_no] += self.connections[file_no].recv(1024)

        if EOL1 in self.requests[file_no] or EOL2 in self.requests[file_no]:
            self.responses[file_no] = callback(self.requests[file_no])
            self.epoll.modify(file_no, select.EPOLLOUT)
            self.connections[file_no].setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)

    def write_to_connection(self, file_no):
        raw_response = self.connections[file_no].send(self.responses[file_no])
        self.responses[file_no] = self.responses[file_no][raw_response:]
        if len(self.responses[file_no]) == 0:
            self.connections[file_no].setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 0)
            self.epoll.modify(file_no, 0)
            self.connections[file_no].shutdown(socket.SHUT_RDWR)

    def close_connection(self, file_no):
        self.epoll.unregister(file_no)
        self.connections[file_no].close()
        del self.connections[file_no]

    def close(self):
        self.epoll.unregister(self.sckt.fileno())
        self.epoll.close()
        self.sckt.close()
