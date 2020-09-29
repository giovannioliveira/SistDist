# interpreta arquivo de config
import configparser
# (de)codifica objetos json
import json
# agente de envio de mensagens
from messaging import MessageAgent

# le config do arquivo
config = configparser.RawConfigParser()
config.read('./config')

# funcao para tratamento de recebimento de mensagem
def handle_message(payload):
    # printa objeto em json na stdout
    print(json.dumps(payload))

# callback de eventos no agente de mensagens
def on_event(event_type, payload):
    # usuario adicionado
    if event_type == MessageAgent.EVENT_JOIN:
        print('user joined: %s' % payload)
    # usuario removido
    elif event_type == MessageAgent.EVENT_LEAVE:
        print('user left: %s' % payload)
    # nova mensagem
    elif event_type == MessageAgent.EVENT_MESSAGE:
        handle_message(payload)


agent = MessageAgent(config, on_event)

while True:
    cmd = input()
    # lista usuarios ativos
    if cmd == 'list':
        print(str(agent.getUsers()))
    # envia mensagem
    elif cmd == 'send':
        users = agent.getUsers()
        try:
            # le index de contato no menu de opcoes exibido para o usuario
            useridx = int(input('choose an user index ('+str({index: value for index, value in enumerate(users)}) + '): '))
            # le mensagem a ser enviada
            message = input('type a message: ')
            # envia mensagem transiente ou exibe falha no envio e motivo
            agent.sendMessage(users[useridx], message)
        except:
            print('error sending message')
    else:
        print('invalid command')

