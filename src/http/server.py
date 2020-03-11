import io
import select
from email.parser import Parser
from multiprocessing import Process

from src.http import HTTPError, DEFAULT_ENCODING
from src.http.request import Request, GET, HEAD
from src.http.response import Response
from src.http.tcp_socket import EpollServerSocket
from src.http.utils import get_response_file


class HTTPServer:
    def __init__(self, host: str, port: int, name: str, root_dir: str, workers: int):
        self._host = host
        self._port = port
        self._name = name
        self._root_dir = root_dir
        self._workers = workers
        self.server_socket = EpollServerSocket(self._host, self._port)

    def run(self):
        workers = [Process(target=self.serve) for _ in range(self._workers)]
        try:
            for w in workers:
                w.start()
            for w in workers:
                w.join()
        finally:
            for w in workers:
                w.terminate()

    def serve(self):
        epoll = self.register_epoll(self.server_socket.sckt.fileno())
        connections = {}
        try:
            while True:
                self._serve_loop(epoll, connections)
        finally:
            while connections:
                self._serve_loop(epoll, connections, shutdown=True)
            self.server_socket.close(epoll)

    def _serve_loop(self, epoll, connections, shutdown=False):
        for file_descriptor, event in epoll.poll(1):
            if not shutdown and file_descriptor == self.server_socket.sckt.fileno():
                self.server_socket.register_connection(connections, epoll)
            elif event & select.EPOLLIN:
                self.server_socket.read_from_connection(connections, epoll, file_descriptor, self.handle_request)
            elif event & select.EPOLLOUT:
                self.server_socket.write_to_connection(connections, epoll, file_descriptor)
            elif event & select.EPOLLHUP:
                self.server_socket.close_connection(connections, epoll, file_descriptor)

    @staticmethod
    def register_epoll(fd):
        epoll = select.epoll()
        epoll.register(fd, select.EPOLLIN)
        return epoll

    @staticmethod
    def _parse_request_line(file: io.BytesIO) -> (str, str, str):
        line = file.readline()
        req_line = str(line, DEFAULT_ENCODING)
        req_line = req_line.rstrip('\r\n')

        words = req_line.split()
        if len(words) != 3:
            raise HTTPError(400, 'Malformed request row')

        method, target, version = words
        if version not in ('HTTP/1.0', 'HTTP/1.1'):
            raise HTTPError(400, 'Unexpected protocol version')
        return method, target, version

    @staticmethod
    def _parse_headers(file: io.BytesIO) -> str:
        headers = []
        while True:
            line = file.readline()
            if line in (b'\r\n', b'\n', b''):
                break  # end of headers
            headers.append(line)
        str_headers = b''.join(headers).decode(DEFAULT_ENCODING)
        return Parser().parsestr(str_headers)

    def _parse_request(self, binary_data: bytes) -> Request:
        with io.BytesIO(binary_data) as file:
            method, target, version = self._parse_request_line(file)
            headers = self._parse_headers(file)
            return Request(method, target, version, headers, file)

    @staticmethod
    def _build_error_response(err: Exception, status: int, reason: str) -> Response:
        body = str(err).encode(DEFAULT_ENCODING)
        return Response(status, reason, [('Content-Length', len(body))], body)

    @staticmethod
    def _build_success_response(root_dir: str, path: str, method: str) -> Response:
        response_file = get_response_file(root_dir, path)
        headers = [
            ('Content-Type', response_file.content_type),
            ('Content-Length', response_file.length),
        ]
        file = response_file.file if method == GET else None
        return Response(200, 'OK', headers=headers, file=file)

    def handle_request(self, binary_data: bytes) -> Response:
        try:
            request = self._parse_request(binary_data)
            if request.method not in (GET, HEAD):
                return Response(405, 'Method not allowed')
            return self._build_success_response(self._root_dir, request.path, request.method)
        except HTTPError as err:
            return self._build_error_response(err, err.status, err.reason)
        except Exception as err:
            return self._build_error_response(err, 500, 'Internal Server Error')
