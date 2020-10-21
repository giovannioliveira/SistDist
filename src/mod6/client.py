import xmlrpc.client

while True:
    cmd = input().split(' ')
    try:
        if cmd[0] == 'get':
           with xmlrpc.client.ServerProxy("http://localhost:"+cmd[2]) as proxy:
                print(proxy.get_key(cmd[1]))
        elif cmd[0] == 'set':
           with xmlrpc.client.ServerProxy("http://localhost:"+cmd[3]) as proxy:
                print(proxy.set_key(cmd[1], cmd[2]))
        else:
            raise None
    except:
        print('bad arguments')
