import socket


def create_server_socket(host='127.0.0.1', port=53210):
    serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    serv_socket.bind((host, port))
    serv_socket.listen()
    return serv_socket


def accept_connection(serv_socket, cid):
    clnt_socket, clnt_addr = serv_socket.accept()
    print(f'Client #{cid} connected by {clnt_addr[0]}:{clnt_addr[1]}')
    return clnt_socket


if __name__ == '__main__':
    server_socket = create_server_socket()
    while True:
        client_socket = accept_connection(server_socket, 0)
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            client_socket.sendall(data)
        client_socket.close()
