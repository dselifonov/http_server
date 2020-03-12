import mimetypes
import os


class Body:
    def __init__(self, path: str, file):
        self.path = path
        self.file = file

    @property
    def content_type(self) -> str:
        return mimetypes.guess_type(self.path)[0]

    @property
    def length(self) -> int:
        return os.path.getsize(self.path)
