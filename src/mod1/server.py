#!/usr/bin/env python3

import socket

IP = 'localhost'
PORT = 12346
MAX_LEN = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((IP, PORT))
    sock.listen()
    print('Listening on ', IP, ":", PORT)
    conn, addr = sock.accept()
    with conn:
        print('Accepted connection from: ', addr)
        while True:
            data = conn.recv(MAX_LEN)
            print('Received: ', str(data, encoding='utf-8'))
            # a string vazia encerra a conexão
            if not data:
                print("Got exit message")
                break
            conn.send(data)
        print('Closing connection')
        conn.close()
    print('Closing socket')
    sock.close()
