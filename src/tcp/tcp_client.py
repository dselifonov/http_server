import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(('127.0.0.1', 53210))
client_socket.sendall(b'Hello World!!!')

data = client_socket.recv(1024)

client_socket.close()

print('Received ', repr(data))
