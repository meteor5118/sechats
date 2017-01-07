#!/usr/bin/env python
"""bhnet

Usage:
    bhnet.py -p PORT [-t HOST] [-l] [-e FILE_TO_RUN] [-c] [-u DESTINATION]

Options:
    -l --listen                             listen on host:port for incoming connections
    -e FILE_TO_RUN --execute=FILE_TO_RUN    execute the given file upon receiving a connection
    -c --command                            initialize a command shell
    -u DESTINATION --upload=DESTINATION     upon receiving connection upload a file and write to [destination]

"""

import sys
import socket
import threading
import subprocess
from docopt import docopt


listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def client_sender(data):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if data:
            client.send(data)

        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response,

            buf = raw_input("")
            buf += '\n'

            client.send(buf)
    except:
        print 'Except!'
        client.close()


def run_command(cmd):
    cmd = cmd.rstrip()

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute %s\r\n" % cmd

    return output


def client_handler(client_socket):

    if upload_destination:
        file_buffer = ''

        while True:
            data = client_socket.recv(1024)

            if data:
                file_buffer += data
            else:
                break

        try:
            file_handle = open(upload_destination, 'wb')
            file_handle.write(file_buffer)
            file_handle.close()

            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    if execute:
        output = run_command(execute)

        client_socket.send(output)

    if command:
        while True:
            client_socket.send("<BHP:#> ")

            cmd_buffer = ""

            while '\n' not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

                response = run_command(cmd_buffer)

                client_socket.send(response)


def server_loop():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        handler = threading.Thread(target=client_handler, args=(client_socket,))
        handler.start()


def main():
    global listen
    global command
    global execute
    global target
    global port
    global upload_destination

    arguments = docopt(__doc__)

    # print arguments

    listen = arguments['--listen']
    command = arguments['--command']
    upload_destination = arguments['--upload']
    target = arguments['HOST'] or '0.0.0.0'
    port = int(arguments['PORT'])
    execute = arguments['--execute']

    # tcp client
    if not listen and target and port > 0:
        data = sys.stdin.read()

        client_sender(data)

    # tcp server
    if listen:
        server_loop()


main()
