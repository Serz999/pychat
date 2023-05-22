from sys import argv
from server import ChatServer
from client import  ChatClient 


if __name__ == '__main__':
    command, host, port = argv[1], argv[2], argv[3]
    if command == 'runserver':
        app = ChatServer(host, port) 
    elif command == 'startchat':
        app = ChatClient(host, port)
        
