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
    def __init__(self, name: str, extension: str, data: bytes = None):
        self.name = name
        self.extension = extension
        self.data = data

    @property
    def content_type(self) -> str:
        return CONTENT_TYPES.get(self.extension, 'application/octet-stream')

    @property
    def length(self) -> int:
        return len(self.data) if self.data else 0
