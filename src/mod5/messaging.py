import socket
import threading
from datetime import datetime
from time import sleep
import ipaddress
import json

class MessageAgent:

    EVENT_JOIN = 'JOIN'
    EVENT_LEAVE = 'LEFT'
    EVENT_MESSAGE = 'MESSAGE'

    def __init__(self, config, on_event):
        self.config = config
        # le configuracoes de objeto de config
        self.ip = config['NETWORK']['Ip']
        self.subnet = ipaddress.ip_network(config['NETWORK']['Subnet'])
        self.port = int(config['NETWORK']['Port'])
        self.pollingTimeoutSecs = int(config['ADJUST']['PollingTimeoutSecs'])
        self.deadUserThresholdSecs = int(config['ADJUST']['DeadUserThresholdSecs'])
        self.on_event = on_event
        # dicionario de usuarios com tempo do ultimo heartbeat
        self.users = {}
        # exclusao mutua na manipulacao do dicionario de usuarios
        self.lock = threading.Lock()
        # servidor TCP para receber mensagens de outros usuarios
        self.TCPServer = threading.Thread(target=self.receiveMessage)
        self.TCPServer.start()
        # thread para emitir heartbeat do usuario
        self.publisher = threading.Thread(target=self.publishSelf)
        self.publisher.start()
        # servidor UDP para receber heartbeats de outros usuarios
        self.UDPServer = threading.Thread(target=self.listenUDP)
        self.UDPServer.start()

    # retorna usuarios ativos
    def getUsers(self):
        return list(self.users.keys())

    # envia mensagem para usuario especificado
    def sendMessage(self, user, message):
        # usuario ficou inativo no meio da operacao
        if user not in self.users:
            raise Exception('user not found')
        # envia mensagem através de pacote(s) TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # conecta ao servidor TCP do destinatario
            sock.connect((user, self.port))
            # codifica objeto json
            sock.sendall(json.dumps({'from': self.ip, 'message': message}).encode())

    # recebe mensagens destinadas ao usuario
    def receiveMessage(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # abre socket TCP em IP unicast
            sock.bind((self.ip, self.port))
            sock.listen()
            while True:
                # aceita conexao
                conn, addr = sock.accept()
                buffer = ''
                # le bytes ate o fim da conexao
                while True:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    # decodifica chunk
                    buffer += str(chunk, encoding='utf-8')
                # fecha conexao
                conn.close()
                # decodifica objeto json
                obj = json.loads(buffer)
                # notifica callback da ocorrencia do evento
                self.on_event(self.EVENT_MESSAGE, obj)

    # recebe heartbeats de outros usuarios
    def listenUDP(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # abre socket UDP em IP de broadcast
            sock.bind((str(self.subnet.broadcast_address), self.port))
            while True:
                # endereco o emissor do pacote UDP de conteudo desprezado
                addr = sock.recvfrom(0)[1][0]
                # notifica se o usuario e novo
                if addr not in self.users:
                    self.on_event(self.EVENT_JOIN, addr)
                # atualiza registro na lista de usuarios
                self.lock.acquire()
                self.users[addr] = datetime.now()
                self.lock.release()

    # emite heartbeat e gerencia o registro de atividade de usuarios
    def publishSelf(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind((self.ip, self.port))
                # habilita o modo de envio em broadcast
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                # envia heartbeat para endereco broadcast
                sock.sendto(bytes(), (str(self.subnet.broadcast_address), self.port))
                # controla latencia de heartbeat
                sleep(self.pollingTimeoutSecs)
            self.lock.acquire()
            rmusers = []
            for user in self.users:
                # usuarios mais antigos que o limiar sao adicionados na lista de dead-nodes
                if (datetime.now() - self.users[user]).seconds > self.deadUserThresholdSecs:
                    rmusers.append(user)
            # dead-nodes sao removidos e um evento e emitido
            for user in rmusers:
                self.on_event(self.EVENT_LEAVE, user)
                del self.users[user]
            self.lock.release()
