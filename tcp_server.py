import socket
import threading


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(('0.0.0.0', 9999))

server.listen(5)

def handle_client(client_socket):
    request = client_socket.recv(4096)

    print 'Received: \n', request

    client_socket.send('ACK')

    client_socket.close()

while True:
    client, addr = server.accept()

    print "Accepted from: %s:%d" % (addr[0], addr[1])

    client_handler = threading.Thread(target=handle_client, args=(client, ))
    client_handler.start()
