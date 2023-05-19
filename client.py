from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from .entities import Envelope
import pickle


class ChatClient:
    def __init__(self, host, port) -> None:
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.server_addr = (host, int(port))
        self.user_name: str
        self.current_receiver = None
        self.__startchat()

    def __startchat(self) -> None:
        self.sock.connect(self.server_addr)
         
        std_in_th = Thread(target=self.__write_messages)
        std_in_th.start()
         
        std_out_th = Thread(target=self.__read_messages)
        std_out_th.start()

    def __write_messages(self) -> None:
        while True:
            message = input('>')
            envelope = Envelope(self.user_name, self.current_receiver, message)
            self.sock.send(pickle.dumps(envelope))
         
    def __read_messages(self) -> None:
        while True:
            response = pickle.loads(self.sock.recv(1024))
            print(response)
          
