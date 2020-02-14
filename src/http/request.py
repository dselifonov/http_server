from functools import lru_cache
from urllib.parse import urlparse

GET = 'GET'
HEAD = 'HEAD'


class Request:
    def __init__(self, method: str, target: str, version: str, headers: str, file):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.file = file

    @property
    @lru_cache(maxsize=None)
    def url(self):
        return urlparse(self.target)

    @property
    @lru_cache(maxsize=None)
    def query(self) -> str:
        return self.url.query

    @property
    def path(self) -> str:
        return self.url.path
