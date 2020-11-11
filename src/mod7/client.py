import xmlrpc.client

while True:
    cmd = input().split(' ')
    try:
        with xmlrpc.client.ServerProxy("http://localhost:" + cmd[1]) as proxy:
            # ex.: get 47123 (lê valor no nó 47123)
            if cmd[0] == 'get':
                print(proxy.get_value())
            # ex.: get 47123 10 (define valor como 10 no nó 47123)
            elif cmd[0] == 'set':
                print(proxy.set_value(cmd[2]))
            # ex.: get 47123 (lê valor no nó 47123)
            elif cmd[0] == 'history':
                print(proxy.get_history())
            elif cmd[0] == 'publish':
                print(proxy.publish_result())
            else:
                raise None
    except:
        print('exception')
