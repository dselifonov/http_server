import datetime

from src.http import DEFAULT_ENCODING


class Response:
    default_headers = [
        ('Date', datetime.datetime.now()),
        ('Server', 'DS Software ltd. (Unix)'),
        ('Connection', 'close')
    ]

    def __init__(self, status: int, reason: str, headers=None, file=None):
        self.status = status
        self.reason = reason
        self.headers = Response.default_headers + (headers or [])
        self.file = file
        self.cursor = 0
        self.definition_sent = False

    def send_response_definition(self):
        self.definition_sent = True

        bin_resp = b''
        bin_resp += f"HTTP/1.1 {self.status} {self.reason}\r\n".encode(DEFAULT_ENCODING)
        for (k, v) in self.headers:
            header_line = f"{k}: {v}\r\n"
            bin_resp += header_line.encode(DEFAULT_ENCODING)
        return bin_resp + b'\r\n'

    def read_body_by_chunks(self, chunk_size=1024):
        if not self.file:
            return
        while True:
            self.file.seek(self.cursor)
            data = self.file.read(chunk_size)
            self.file.seek(self.cursor)
            if not data:
                break
            yield data
        self.cursor = 0
        self.file.close()
