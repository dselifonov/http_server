import sys
import threading

from src.tcp import read_request, handle_request, write_response
from src.tcp.tcp_server import create_server_socket, accept_connection


def serve_client(client_socket, cid):
    request = read_request(client_socket)
    if request is None:
        print(f"Client #{cid} disconnected.")
        return
    response = handle_request(request)
    write_response(client_socket, response, cid)


def run_server(port=53210):
    server_socket = create_server_socket(port)
    cid = 0

    while True:
        client_socket = accept_connection(server_socket, cid)
        threading.Thread(target=serve_client, args=(client_socket, cid)).start()
        cid += 1


if __name__ == '__main__':
    run_server(port=int(sys.argv[1]))
