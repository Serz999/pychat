from logging import log
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from models import Envelope, Client
from chat_storage import ChatPostgresStorage
import pickle
from enum import Enum
from datetime import datetime

 
class ChatServer: 
    std_out_lock = Lock()
    avail_commands = [
        '/login', '/register', '/help', '/members', 
        '/chatwith', '/history', '/exit'
    ]

    def __init__(self, host, port) -> None:
        self.addr = (host, int(port))
        self.sock = socket(AF_INET, SOCK_STREAM) 
        self.curr_connections = {}
        self.db = ChatPostgresStorage()
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
            envelope = self.recv_envelope(conn)
            first_word = str(envelope.load).split(' ')[0]
            if first_word in ChatServer.avail_commands:
                self.__commands_handle(conn, envelope)
            else:
                conn = self.curr_connections[str(envelope.recevier)]
                self.send_evnelope(conn, envelope, db_record=True) 
                with ChatServer.std_out_lock:
                    print(f'-- Send message from "{envelope.sender}" '\
                            f'to "{envelope.recevier}" :: "{envelope.load}"')
    
    def recv_envelope(self, conn: socket) -> Envelope:
        data = conn.recv(1024)
        envelope = pickle.loads(data)
        return envelope

    def send_evnelope(self, conn: socket, envelope: Envelope, db_record=False) -> None:
        if db_record: 
            self.db.add_envelope(envelope)
            if str(envelope.recevier) in self.curr_connections:
                data = pickle.dumps(envelope)
                conn.send(data)
        else:
            data = pickle.dumps(envelope)
            conn.send(data)
 
    def __commands_handle(self, conn: socket, envelope: Envelope) -> None:
        with ChatServer.std_out_lock:
            print('~~ Oh, this mesagge for me!')
        command = str(envelope.load).split(' ')[0]
        if command == '/login': 
            self.__login_handle(conn, envelope) 
        elif command == '/register':
            self.__register_handle(conn, envelope) 
        elif command == '/help':
            self.__get_help_handle(conn, envelope)
        elif command == '/members':
            self.__get_members_handle(conn, envelope)
        elif command == '/chatwith':
            self.__chat_with_handle(conn, envelope)
        elif command == '/history':
            self.__get_history_handle(conn, envelope)
        elif command == '/exit':
            self.__exit_handle(conn, envelope)

    def __login_handle(self, conn:socket, envelope:Envelope) -> None:
        message = str(envelope.load).split(' ')
        login, passwd = message[1], message[2]
        if self.db.auth_member(login, passwd):
            self.curr_connections[login] = conn
            envelope.load = self.db.get_members(login=login)[0]
            envelope.recevier = envelope.load
            self.send_evnelope(conn, envelope)
            print(f'~~ Auth: User "{envelope.load}" has been authorized!')
        else: 
            envelope.load = False
            self.send_evnelope(conn, envelope)
            print(f'~~ Auth error: incorrect login or password.')

    def __register_handle(self, conn: socket, envelope: Envelope) -> None:
        message = str(envelope.load).split(' ')
        login, passwd = message[1], message[2]
        if self.db.reg_member(login, passwd):
            self.curr_connections[login] = conn
            envelope.load = self.db.get_members(login=login)[0]
            envelope.recevier = envelope.load
            self.send_evnelope(conn, envelope)
            print(f'~~ Reg: User "{envelope.load}" has been created!')
        else: 
            envelope.load = False
            self.send_evnelope(conn, envelope) 
            print(f'~~ Reg error: User with login "{login}" already exist.')

    def __get_members_handle(self, conn: socket, envelope: Envelope) -> None:
        message = str(envelope.load).split(' ')
        if len(message) < 2:
            envelope.load = 'command /massage req 1 arg, enter /help to more informaiton'
            self.send_evnelope(conn, envelope)
        else:
            arg = message[1]
            member_list = []
            if arg == 'all':
                member_list = self.db.get_members()
            else:
                member_list = self.db.get_members(login=arg)
            envelope.load = member_list
            self.send_evnelope(conn, envelope)

    def __chat_with_handle(self, conn: socket, envelope: Envelope) -> None:
        message = str(envelope.load).split(' ')
        if len(message) < 2:
            envelope.load = 'command /chatwith req 1 arg,' \
                            'enter /help to more informaiton'
               
            self.send_evnelope(conn, envelope) 
        else: 
            target_name = message[1]
            target = self.db.get_members(login=target_name)[0]
            envelope.load = target
            self.send_evnelope(conn, envelope)

    def __get_history_handle(self, conn: socket, envelope: Envelope) -> None:
        ...
    
    def __exit_handle(self, conn: socket, envelope: Envelope) -> None:
        envelope.load = envelope.sender
        self.send_evnelope(conn, envelope)
    
    def __get_help_handle(self, conn: socket, envelope: Envelope) -> None:
        envelope.load = f''\
        '=======================HELP=INFO========================\n'\
        '-- /help - print help info\n'\
        '-- /members [all] or [membername] - print chat members\n'\
        '-- /chatwith [memgername] - connect to chat with member\n'\
        '-- /history - print history of chat with current member\n'\
        '-- /exit - exit form chat\n'\
        '========================================================'
        self.send_evnelope(conn, envelope)
