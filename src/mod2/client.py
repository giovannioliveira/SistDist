#!/usr/bin/env python3

import socket
import sys
import json

SERVER_IP = 'localhost'
SERVER_PORT = 12344
MAX_TCP_MESSAGE_LEN = 1024

# define socket como TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # abre conexão com servidor remoto no IP e porta especificadas
    sock.connect((SERVER_IP, SERVER_PORT))
    # executa o loop enquanto não encontra o comando de encerramento de fluxo
    while True:
        sys.stdout.write("Enter with filename: ")
        sys.stdout.flush()
        # lê a entrada na stdin
        line = sys.stdin.readline()[:-1] # removes \n from read line
        # comando para encerrar o fluxo
        if not line:
            print("Got exit message")
            break
        print('Sending message "', line, '" to ', SERVER_IP, ':', SERVER_PORT)
        # envia nome do arquivo codificado em bytes para o servidor
        sock.send(line.encode())
        # aguarda a resposta do servidor
        res = str(sock.recv(MAX_TCP_MESSAGE_LEN), encoding='utf-8')
        # desserializa a respota do servidor para o formato json
        records = json.loads(res)
        # detecta resposta de erro do servidor
        if len(records) == 0:
            print('Server had an error processing the request')
        else:
            print('Server processed request successfully')
            # printa cada item da lista parseada
            for item in records:
                print('Word: '+item['word']+' Count: '+str(item['count']))
    print('Closing socket')
    # fecha socket
    sock.close()
