import configparser
import json

from messaging import MessageAgent

config = configparser.RawConfigParser()
config.read('./config')


def handle_message(payload):
    print(json.dumps(payload))


def on_event(event_type, payload):
    if event_type == MessageAgent.EVENT_JOIN:
        print('user joined: %s' % payload)
    elif event_type == MessageAgent.EVENT_LEAVE:
        print('user left: %s' % payload)
    elif event_type == MessageAgent.EVENT_MESSAGE:
        handle_message(payload)


agent = MessageAgent(config, on_event)

while True:
    cmd = input()
    if cmd == 'list':
        print(str(agent.getUsers()))
    elif cmd == 'send':
        users = agent.getUsers()
        useridx = int(input('choose an user index ('+str({index: value for index, value in enumerate(users)}) + '): '))
        message = input('type a message: ')
        agent.sendMessage(users[useridx], message)
    else:
        print('invalid command')

