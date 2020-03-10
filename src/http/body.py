import os

CONTENT_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.swf': 'application/x-shockwave-flash',
}


class Body:
    def __init__(self, path: str, name: str, extension: str, file):
        self.path = path
        self.name = name
        self.extension = extension
        self.file = file

    @property
    def content_type(self) -> str:
        return CONTENT_TYPES.get(self.extension, 'application/octet-stream')

    @property
    def length(self) -> int:
        return os.path.getsize(self.path)
