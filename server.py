from _typeshed import AnyStr_co
from re import A
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from .entities import Envelope, Client
import pickle
from enum import Enum


class AvailableCommands(Enum):
    login = '/login'
    register = '/register'
    get_help = '/help'
    get_members = '/members'
    chat_with = '/chatwith'  # Need to write latest messages, when start chat
    get_history = '/history'
    exit = '/exit'
     

# Docker compose up
class ChatServer:
    std_out_lock = Lock() 

    def __init__(self, host, port) -> None:
        self.addr = (host, int(port))
        self.sock = socket(AF_INET, SOCK_STREAM) 
        self.connections = {}
        self.__runserver()

    def __del__(self) -> None:
        self.sock.close() 

    def __runserver(self):
        self.sock.bind(self.addr) 
        self.sock.listen(10)
        print('Server is running, please, press ctrl+c to stop')
        while True:
            conn, addr = self.sock.accept()
            print(f'-- {addr[0]}:{addr[1]} is connected.')
            th = Thread(target=self.__handle_connection, args=(conn, ))
            th.start()
 
    def __handle_connection(self, conn: socket) -> None:
        while True:
            data = conn.recv(1024)
            envelope = pickle.loads(data)
            message = envelope.message
            first_word = message[:message.find(' ')]
            if first_word in AvailableCommands:
                self.__commands_handle(conn, envelope)
            else:
                self.connections[envelope.recevier].send(pickle.dumps(envelope))
                with ChatServer.std_out_lock:
                    print(f'-- Send message from "{envelope.sender}"'\
                                            f'to "{envelope.recevier}".')
    
    def __commands_handle(self, conn, envelope: Envelope) -> None:
        with ChatServer.std_out_lock:
            print('~~ Oh, this mesagge for me!')
        message = envelope.message.split(' ')
        command = message[0]
        if command == AvailableCommands.login:
            login, passwd = message[1], message[2]
            with ChatServer.std_out_lock:
                print(f'~~ Try to sign in user "{envelope.sender}".')
            if self.__login(login, passwd):
                response = Envelope('server', envelope.sender, 'SUCCESS')
                conn.send(pickle.dumps(response))
            else:
                response = Envelope('server', envelope.sender, 'ERROR')
                conn.send(pickle.dumps(response))
        elif command == AvailableCommands.register:
            login, passwd = message[1], message[2]
            if self.__register(login, passwd):
                response = Envelope('server', envelope.sender, 'SUCCESS')
                conn.send(pickle.dumps(response))
            else:
                response = Envelope('server', envelope.sender, 'ERROR')
                conn.send(pickle.dumps(response))
        elif command == AvailableCommands.get_help:
            help = self.__get_help()
        elif command == AvailableCommands.get_members:
            members = self.__get_members()
        elif command == AvailableCommands.chat_with:
            self.__chat_with()  
        elif command == AvailableCommands.get_history:
            history = self.__get_history()
        elif command == AvailableCommands.exit:
            self.__exit()

    def __login(self, login, passwd) -> bool:
        ...

    def __register(self, login, passwd) -> bool: 
        ...

    def __get_help(self) -> dict:
        ...

    def __get_members(self) -> dict:
        ...

    def __chat_with(self) -> bool:
        ...

    def __get_history(self) -> dict:
        ...

    def __exit(self) -> None:
        ...
    
