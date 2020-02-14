import datetime
import io
import select
from email.parser import Parser

from src.http import HTTPError
from src.http.request import Request, GET, HEAD
from src.http.response import Response
from src.http.tcp_socket import EpollServerSocket
from src.http.utils import get_response_file

DEFAULT_ENCODING = 'iso-8859-1'


class HTTPServer:
    def __init__(self, host: str, port: int, name: str, root_dir: str, workers: int):
        self._host = host
        self._port = port
        self._name = name
        self._root_dir = root_dir
        self._workers = workers

    def serve(self):
        server_socket = EpollServerSocket(self._host, self._port)
        try:
            while True:
                for file_descriptor, event in server_socket.events:
                    if file_descriptor == server_socket.sckt.fileno():
                        server_socket.register_connection()
                    elif event & select.EPOLLIN:
                        server_socket.read_from_connection(file_descriptor, self.handle_request)
                    elif event & select.EPOLLOUT:
                        server_socket.write_to_connection(file_descriptor)
                    elif event & select.EPOLLHUP:
                        server_socket.close_connection(file_descriptor)
        finally:
            server_socket.close()

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

        print(f"{method} {target} {version} -> ", end="")
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
        body = response_file.data if method == GET else None
        return Response(200, 'OK', headers=headers, body=body)

    def _build_response(self, binary_data: bytes) -> Response:
        try:
            request = self._parse_request(binary_data)
            if request.method not in (GET, HEAD):
                return Response(405, 'Method not allowed')
            return self._build_success_response(self._root_dir, request.path, request.method)
        except HTTPError as err:
            return self._build_error_response(err, err.status, err.reason)
        except Exception as err:
            return self._build_error_response(err, 500, 'Internal Server Error')

    @staticmethod
    def _write_headers(response: Response) -> bytes:
        bin_resp = b''
        default_headers = [
            ('Date', datetime.datetime.now()),
            ('Server', 'DS Software ltd. (Unix)'),
            ('Connection', 'close')
        ]
        headers = response.headers + default_headers if response.headers else default_headers
        for (k, v) in headers:
            header_line = f"{k}: {v}\r\n"
            bin_resp += header_line.encode(DEFAULT_ENCODING)
        return bin_resp + b'\r\n'

    def handle_request(self, binary_data: bytes) -> bytes:
        response = self._build_response(binary_data)
        binary_response = b''
        binary_response += f"HTTP/1.1 {response.status} {response.reason}\r\n".encode(DEFAULT_ENCODING)
        binary_response += self._write_headers(response)
        if response.body:
            binary_response += response.body
        print(f"{response.status} {response.reason}")
        return binary_response
