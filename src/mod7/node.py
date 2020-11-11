import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import threading
import random
import time
import sys

init_port = 47123
n_nodes = 4


class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class Node:

    def __init__(self, port, nodes, initial_primary):
        self.port = port
        self.clients = {node: xmlrpc.client.ServerProxy('http://localhost:' + str(node)) for node in nodes}
        self.server = SimpleThreadedXMLRPCServer(("localhost", port))
        self.server.register_instance(self)
        self.lock = threading.Lock()
        self.primary = initial_primary
        self.history = []
        self.release = False
        self.acquiring = True
        self.changes = False

    def get_value(self):
        self.log('get_value called')
        return self.history[-1][1] if len(self.history) > 0 else 0

    def set_value(self, value):
        self.log('set_value called with arg=' + str(value))
        if self.primary == self.port and not self.release:
            self.history.append((self.port, value))
            self.changes = True
            self.log('push update to local history ' + str(self.history[-1]))
            return True
        else:
            while not self.acquire_primary():
                rand = random.uniform(0, 2)
                print('failed acquiring, sleeping ' + str(rand) + ' secs')
                time.sleep(rand)
            self.set_value(value)
            return True

    def listen_result(self, result):
        self.history.append(result)
        self.primary = result[0]
        return True

    def publish_result(self):
        if not self.changes or self.primary != self.port:
            self.log('no changes to commit')
            self.release = True
            return True
        for key in self.clients:
            if key != self.port:
                try:
                    self.clients[key].listen_result(self.history[-1])
                except:
                    self.log('exception: ' + str(sys.exc_info()[0]))
                    self.log('error publishing result to node=' + str(key))
                    return False
        self.log('published changes')
        self.release = True
        return True

    def transfer_primary(self, node):
        self.log('transfer primary from node=')
        with self.lock:
            self.log('acquite l')
            if self.port != self.primary or not self.release:
                self.log('ask denied. primary=' + str(self.primary))
                return [False, self.primary]
            else:
                self.primary = node
                return [True, node]

    def acquire_primary(self):
        with self.lock:
            if self.primary == self.port and self.release:
                self.log('relocking primary status')
                self.release = False
                self.changes = False
                return True

            self.log('trying to acquire primary status from '+str(self.primary))
            try:
                resp = self.clients[self.primary].transfer_primary(self.port)
                self.log('acquire answer: '+str(resp))
                if resp[0]:
                    self.primary = self.port
                    self.release = False
                    self.changes = False
                    return True
                else:
                    self.primary = resp[1]
                    return False
            except:
                self.log('exception: ' + str(sys.exc_info()[0]))
                return False

    def release_primary(self):
        if self.primary != self.port:
            self.log('not primary to release')
            return False
        else:
            self.log('releasing primary')
            self.release = True
            return True

    def serve(self):
        self.server.serve_forever()

    def log(self, message):
        print(str(self.port) + ': ' + str(message))

    def get_history(self):
        return self.history


nodes = {port: None for port in range(init_port, init_port+n_nodes, 1)}
ports = tuple(nodes.keys())
for port in ports:
    nodes[port] = Node(port, ports, init_port)
    threading.Thread(target=lambda: nodes[port].serve()).start()
