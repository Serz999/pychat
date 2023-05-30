from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from models import Envelope, Client
import pickle
from time import sleep


class ChatClient:
    def __init__(self, host, port) -> None:
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.server_addr = (host, int(port))
        self.user: Client
        self.curr_recv: Client
        self.__startchat()
    
    def __del__(self) -> None:
        self.sock.close()

    def __startchat(self) -> None:
        self.sock.connect(self.server_addr)  
        self.__init_login_loop()
        self.curr_recv = self.user
        print('---  now you in the <main menu>  ---')
        std_in_th = Thread(target=self.__write_messages)
        std_out_th = Thread(target=self.__read_messages)
        std_in_th.start()
        std_out_th.start()
 
    def __init_login_loop(self) -> None:
        run = True
        while run:
            login = input('login>')
            passwd = input('passwd>')
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f'/login {login} {passwd}'
            envelope = Envelope(
                    Client(0,''), 
                    Client(0,''), 
                    time, message)
            self.send_evnelope(envelope) 
            resp_envelope = self.recv_envelope()
            if isinstance(resp_envelope.load, Client):
                self.user = resp_envelope.load
                print(f'Welcome, {self.user}!')
                run = False
            else:
                print('Invalid username or password.')
                print('Maybe you want to create a new account?')
                res = input('Yes/No>')
                if res == 'Yes' or res == 'Y' or res == 'y' or res == 'yes':
                    new_login = input('new-login>')
                    passwd = input('passwd>')
                    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    message = f'/register {new_login} {passwd}'
                    envelope = Envelope(
                            Client(0,''), 
                            Client(0,''), 
                            time, message)
                    self.send_evnelope(envelope) 
                    resp_envelope = self.recv_envelope()
                    if isinstance(resp_envelope.load, Client):
                        self.user = resp_envelope.load
                        print(f'User "{self.user}" was created!')
                        print(f'Welcome, {self.user}!')
                        run = False
                    else:
                        print(f'User with name "{new_login}" already exist.')
     
    def send_evnelope(self, envelope: Envelope) -> None:
        data = pickle.dumps(envelope)
        self.sock.send(data)   
     
    def recv_envelope(self) -> Envelope:
        data = self.sock.recv(1024)
        envelope = pickle.loads(data)
        return envelope
     
    def __write_messages(self) -> None:
        while True:
            message = input()
            if '/exit' in message:
                self.curr_recv = self.user
                print(f'---  return to the <main menu>  ---')
                continue 
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            envelope = Envelope(self.user, self.curr_recv, time, message)  
            self.send_evnelope(envelope)
     
    def __read_messages(self) -> None:
        while True:
            envelope = self.recv_envelope()
            self.__interpritate_envelope(envelope)
                 
    def __interpritate_envelope(self, envelope: Envelope):
        if isinstance(envelope.load, list):
            items = envelope.load
            if items:
                if isinstance(items[0], Client):
                    print('===========CHAT=MEMBERS==========')
                    for m in items:
                        print(f'-- id: {m.id} name: {m.login}')
                    print('=================================') 
        elif isinstance(envelope.load, tuple):
            self.curr_recv = envelope.load[0]
            if envelope.load[0] == self.user:
                print(f'---  return to the <main menu>  ---')
            else: 
                print(f'--- start chatwith <{self.curr_recv}> ---')
                for e in envelope.load[1]:
                    print(f'{self.curr_recv}>{e.load}')
        elif isinstance(envelope.load, str):
            if envelope.sender == self.user:
                print(f'{envelope.load}')
            elif envelope.sender == self.curr_recv:
                print(f'{self.curr_recv}> {envelope.load}')
                envelope.load = '/accept'
                self.send_evnelope(envelope)

