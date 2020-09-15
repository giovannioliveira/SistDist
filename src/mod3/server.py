#!/usr/bin/env python3

import socket
import json
import select
import sys
import threading

IP = 'localhost'
PORT = 12344
MAX_TCP_MESSAGE_LEN = 1024
MAX_WORDS_IN_RESULT = 10

# var to store watched descriptors in main thread
descriptors = [sys.stdin]
# var to store current connections in child threads
connections = {}
# lock to sync child threads
lock = threading.Lock()

# working thread to attend client requests
def acceptConnection(sock):
    # accepts a new connection
    conn, addr = sock.accept()
    with conn:
        # register connection in global list thread-safely
        lock.acquire()
        connections[addr] = conn
        lock.release()
        print('Accepted connection from: ', addr)
        while True:
            # lê os bytes enviados pelo cliente
            data = conn.recv(MAX_TCP_MESSAGE_LEN)
            # a string vazia encerra a conexão
            if not data:
                print("Got exit message")
                break
            # converte resultado em bytes para string
            datastr = str(data, encoding='utf-8')
            print('Received: ', datastr)
            # operação lança exception se arquivo está inacessível (sem permissão ou arquivo inexistente)
            try:
                # tenta abrir o arquivo no modo leitura
                with open('files/' + datastr, 'r') as file:
                    # remove quebras de linhas
                    content = file.read().replace('\n', ' ')
                    # tokeniza as palavras presentes no documento
                    content = content.split(" ")
                    # cria um conjunto com a lista de palavras presentes no texto
                    contentSet = set(content)
                    if '' in contentSet:
                        contentSet.remove('')
                    wordCount = []
                    # para cada palavra distinta presente no texto
                    for word in contentSet:
                        # insere na lista um objeto que representa a entrada
                        wordCount.append({'word': word, 'count': content.count(word)})
                    # ordena os registros da lista usando a propriedade count da entrada
                    wordCount.sort(reverse=True, key=(lambda x: x['count']))
                    # serializa o objeto de resultado no formato json e trunca a lista de acordo com a configuração
                    dump = json.dumps(wordCount[:MAX_WORDS_IN_RESULT])
                    print('Processed request successfully: ' + dump)
                    # envia a string de resultado codificada em bytes
                    conn.send(dump.encode())
            except Exception as e:
                # descreve a Exception para ajudar no debug do lado do servidor
                print("Exception: " + str(e))
                # envia resposta vazia para o cliente
                conn.send("{}".encode())
            except:
                print("Exception: unknown")
                conn.send("{}".encode())
        print('Closing connection')
        # encerra conexão atual
        conn.close()

        # remove connection from list thread-safely
        lock.acquire()
        del connections[addr]
        lock.release()

# function to handle cli input commands
def processCommand(cmd,sock):
    # command to finish server
    if(cmd == 'end'):
        # if there's no client hang, close socket and exit application
        if not connections:
            sock.close()
            sys.exit(0)
        # if there are active clients, refuse to exit
        else:
            print('server won\'t quit while there are active connections. '+str(connections.values()))
    # print active connections
    elif(cmd == 'status'):
        print(str(connections.values()))
    # unknown command
    else:
        print('unknown command. available commands: end, status')

# define socket como TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # faz bind do socket no IP e porta especificados
    sock.bind((IP, PORT))
    # inicializa socket
    sock.listen()
    # config sock to non-blocking and add it to descriptor list
    sock.setblocking(False)
    descriptors.append(sock)
    print('Listening on ', IP, ":", PORT)
    while True:
        # wait until there's a new connection request or input in the CLI
        r, w, e = select.select(descriptors, [], [])
        for descriptor in r:
            # if there's a new connection request
            if(descriptor == sock):
                # threat client in a new thread
                threading.Thread(target=acceptConnection, args=(sock,)).start()
            # if there's a new input available in stdin
            elif(descriptor == sys.stdin):
                # process this input command
                processCommand(input(),sock)

    #print('Closing socket')
    #sock.close()
