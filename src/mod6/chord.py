import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import threading
import time

# define número de nós como 2**m
m = 4
n = 2 ** m

# define porta inicial
initPort = 9000


def hashmod(key):
    return hash(key) % n


nodeInfo = {hashmod(port): xmlrpc.client.ServerProxy("http://localhost:" + str(port))
         for port in range(initPort, initPort + n)}


class Node:

    def __init__(self, port):
        self.port = port
        self.this = hashmod(port)
        self.finger = [((self.this + 2 ** i) % n, nodeInfo[(self.this + 2 ** i) % n]) for i in range(m)]
        self.keys = {}
        self.server = SimpleXMLRPCServer(("localhost", port))
        self.server.register_instance(self)

    def set_key(self, key, value):
        keynode = hashmod(key)
        if keynode == self.this:
            self.keys[key] = value
            return self.this
        else:
            for i in range(len(self.finger) - 1):
                cur = self.finger[i]
                nxt = self.finger[i + 1]
                if ((cur[0] < nxt[0] and cur[0] <= keynode < nxt[0]) or
                        (nxt[0] < cur[0] <= keynode < (nxt[0] + n))):
                    return cur[1].set_key(key, value)
            return self.finger[-1][1].set_key(key, value)

    def get_key(self, key):
        keynode = hashmod(key)
        if keynode == self.this:
            if key in self.keys:
                return self.keys[key]
            else:
                return 'undefined'
        else:
            for i in range(len(self.finger) - 1):
                cur = self.finger[i]
                nxt = self.finger[i + 1]
                if ((cur[0] < nxt[0] and cur[0] <= keynode < nxt[0]) or
                        (nxt[0] < cur[0] <= keynode < (nxt[0] + n))):
                    return cur[1].get_key(key)
            return self.finger[-1][1].get_key(key)

    def serve(self):
        self.server.serve_forever()

    def __str__(self):
        return str(self.this) + '(' + str(self.port) + ')' + ' : ' + str(self.keys)

nodes = []

for port in range(initPort, initPort + n):
    node = Node(port)
    nodes.append(node)
    threading.Thread(target=lambda: node.serve()).start()

while True:
    time.sleep(3)
    for node in nodes:
        print(node)
    print('-----------------------------------')
