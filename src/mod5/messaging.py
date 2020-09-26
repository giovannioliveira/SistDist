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
        self.ip = config['NETWORK']['Ip']
        self.subnet = ipaddress.ip_network(config['NETWORK']['Subnet'])
        self.port = int(config['NETWORK']['Port'])
        self.pollingTimeoutSecs = int(config['ADJUST']['PollingTimeoutSecs'])
        self.deadUserThresholdSecs = int(config['ADJUST']['DeadUserThresholdSecs'])
        self.on_event = on_event
        self.users = {}
        self.lock = threading.Lock()
        self.TCPServer = threading.Thread(target=self.receiveMessage)
        self.TCPServer.start()
        self.publisher = threading.Thread(target=self.publishSelf)
        self.publisher.start()
        self.UDPServer = threading.Thread(target=self.listenUDP)
        self.UDPServer.start()

    def getUsers(self):
        return list(self.users.keys())

    def sendMessage(self, user, message):
        if user not in self.users:
            raise Exception('user not found')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((user, self.port))
            sock.sendall(json.dumps({'from': self.ip, 'message': message}).encode())

    def receiveMessage(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.ip, self.port))
            sock.listen()
            while True:
                conn, addr = sock.accept()
                buffer = ''
                while True:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    buffer += str(chunk, encoding='utf-8')
                obj = json.loads(buffer)
                self.on_event(self.EVENT_MESSAGE,obj)

    def listenUDP(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((str(self.subnet.broadcast_address), self.port))
            while True:
                addr = sock.recvfrom(0)[1][0]
                if addr not in self.users:
                    self.on_event(self.EVENT_JOIN, addr)
                self.lock.acquire()
                self.users[addr] = datetime.now()
                self.lock.release()

    def publishSelf(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind((self.ip, self.port))
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(bytes(), (str(self.subnet.broadcast_address), self.port))
                sleep(self.pollingTimeoutSecs)
            self.lock.acquire()
            rmusers = []
            for user in self.users:
                if (datetime.now() - self.users[user]).seconds > self.deadUserThresholdSecs:
                    rmusers.append(user)
            for user in rmusers:
                self.on_event(self.EVENT_LEAVE, user)
                del self.users[user]
            self.lock.release()
