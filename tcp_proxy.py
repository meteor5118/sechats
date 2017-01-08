#!/usr/bin/env python
"""
tcp proxy

Usage:
    tcp_proxy.py <local_host> <local_port> <remote_host> <remote_port> <receive_first>

"""

import sys
import socket
import threading
from docopt import docopt


def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2

    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7f else b'.' for x in s])
        result.append(b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text))

        print b'\n'.join(result)


def request_handler(buf):
    return buf


def response_handler(buf):
    return buf


def receive_from(connection):
    buf = ""

    connection.settimeout(3)

    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break

            buf += data
    except:
        pass

    return buf


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    
    remote_socket.connect((remote_host, remote_port))
    
    if receive_first:
        remote_buffer = receive_from(remote_socket)

        hexdump(remote_buffer)
        
        remote_buffer = response_handler(remote_buffer)
        
        if remote_buffer:
            print "[<==] Sending %d bytes to localhost." % len(remote_buffer)
            client_socket.send(remote_buffer)
            
    while True:
        local_buffer = receive_from(client_socket)

        if local_buffer:
            print "[==>] Received %d bytes from localhost." % len(local_buffer)

            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)

            remote_socket.send(local_buffer)
            print "[==>] Send to remote."

        remote_buffer = receive_from(remote_socket)

        if remote_buffer:
            print "[<==] Received %d bytes from remote." % len(remote_buffer)

            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)

            client_socket.send(remote_buffer)

            print "[<==] Sent to localhost."

        if len(local_buffer) == 0 and len(remote_buffer) == 0:
            client_socket.close()
            remote_socket.close()
            print "[*] No more data. Closing connections."

            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print "[==>] Received incoming connection from %s:%d" % (addr[0], addr[1])

        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))

        proxy_thread.start()

if __name__ == '__main__':
    args = docopt(__doc__)

    # print args

    local_host = args['<local_host>']
    local_port = int(args['<local_port>'])
    remote_host = args['<remote_host>']
    remote_port = int(args['<remote_port>'])
    receive_first = True if 'true' in str(args['<receive_first>']).lower() else False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

