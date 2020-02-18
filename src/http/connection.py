class Connection:
    def __init__(self, client):
        self.client = client
        self.request = b''
        self.response = b''
