#!/usr/bin/env python3

import socket
import sys

SERVER_IP = 'localhost'
SERVER_PORT = 12346
MAX_LEN = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((SERVER_IP, SERVER_PORT))
    while True:
        sys.stdout.write("Enter with your message (empty for exit): ")
        sys.stdout.flush()
        line = sys.stdin.readline()[:-1] # removes \n from read line
        if not line:
            print("Got exit message")
            break
        print('Sending message "', line, '" to ', SERVER_IP, ':', SERVER_PORT)
        sock.send(line.encode())
        res = sock.recv(MAX_LEN)
        print('Received: ', str(res, encoding='utf-8'))
    print('Closing socket')
    sock.close()
