import os
import sys

from src.tcp import read_request, handle_request, write_response
from src.tcp.tcp_server import create_server_socket, accept_connection


def serve_client(client_socket, cid):
    child_pid = os.fork()
    if child_pid:
        client_socket.close()
        return child_pid

    request = read_request(client_socket)
    if request is None:
        print(f"Client #{cid} disconnected.")
        return
    response = handle_request(request)
    write_response(client_socket, response, cid)
    os._exit(0)


def reap_children(active_children):
    for child_pid in active_children.copy():
        child_pid, _ = os.waitpid(child_pid, os.WNOHANG)
        if child_pid:
            active_children.discard(child_pid)


def run_server(port=53210):
    server_socket = create_server_socket(port)
    cid = 0
    active_children = set()

    while True:
        client_socket = accept_connection(server_socket, cid)
        child_id = serve_client(client_socket, cid)
        active_children.add(child_id)
        reap_children(active_children)
        cid += 1


if __name__ == '__main__':
    run_server(port=int(sys.argv[1]))
