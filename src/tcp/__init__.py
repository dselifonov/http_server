import time


def read_request(client_socket, delimiter=b'!'):
    request = bytearray()
    try:
        while True:
            chunk = client_socket.recv(4)
            if not chunk:
                return None
            request += chunk
            if delimiter in request:
                return request
    except ConnectionResetError:
        return None


def handle_request(request):
    time.sleep(5)
    return request[::-1]


def write_response(client_socket, response, cid):
    client_socket.sendall(response)
    client_socket.close()
    print(f"Client #{cid} has been served.")