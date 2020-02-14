class HTTPError(Exception):
    def __init__(self, status: int, reason: str, body=None):
        super()
        self.status = status
        self.reason = reason
        self.body = body

    def __str__(self) -> str:
        return self.body or self.reason
