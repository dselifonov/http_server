import select
import socket

from src.http.connection import Connection

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
CHUNK_SIZE = 1024  # in bytes


class EpollServerSocket:
    def __init__(self, host, port):
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sckt.bind((host, port))
        self.sckt.listen(50)

    def register_connection(self, connections, epoll):
        connection, _ = self.sckt.accept()
        connection.setblocking(False)
        epoll.register(connection.fileno(), select.EPOLLIN)
        connections[connection.fileno()] = Connection(connection)

    @staticmethod
    def read_from_connection(connections, epoll, file_no, callback):
        connections[file_no].request += connections[file_no].client.recv(CHUNK_SIZE)

        if EOL1 in connections[file_no].request or EOL2 in connections[file_no].request:
            connections[file_no].response = callback(connections[file_no].request)
            epoll.modify(file_no, select.EPOLLOUT)
            connections[file_no].client.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)

    @staticmethod
    def write_to_connection(connections, epoll, file_no):
        if not connections[file_no].response.definition_sent:
            connections[file_no].client.send(connections[file_no].response.send_response_definition())
        chunk = next(connections[file_no].response.read_body_by_chunks(CHUNK_SIZE), None)
        if chunk:
            sent_buffer = connections[file_no].client.send(chunk)
            connections[file_no].response.cursor += sent_buffer
        else:
            connections[file_no].client.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 0)
            epoll.modify(file_no, 0)
            connections[file_no].client.shutdown(socket.SHUT_RDWR)

    @staticmethod
    def close_connection(connections, epoll, file_no):
        epoll.unregister(file_no)
        connections[file_no].client.close()
        del connections[file_no]

    def close(self, epoll):
        epoll.unregister(self.sckt.fileno())
        epoll.close()
        self.sckt.close()
