from dataclasses import dataclass
from socket import socket
from typing import Union, Any
from datetime import datetime


@dataclass
class Client:
    id: int
    login: str 

    def __str__(self) -> str:
        return self.login
   

@dataclass
class Envelope:
    sender: Client
    recevier: Client
    date: str
    load: Any
    
    def swap(self):
        tmp = self.sender
        self.sender = self.recevier
        self.recevier = tmp

    def __str__(self) -> str:
        return f'{self.sender}:{self.recevier}:{self.load}'

