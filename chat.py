import socket
from sys import argv


def runserver(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ip, int(port)))
        connections = {'server':sock}
        sock.listen(10)
        print('Server is running, please, press ctrl+c to stop')
        while True:
            conn, addr = sock.accept() 
            print(f'-- {addr[0]}:{addr[1]} is connected.')
            while True:
                envelop = conn.recv(1024).decode()
                sender, recevier, message = envelop.split(':')
                if recevier == 'server':
                    print('~~ Oh, this mesagge for me!')
                    if message == 'login':
                        print(f'~~ Try to sign in user "{sender}".')
                        connections[sender] = conn
                        conn.send(bytes('Success!', encoding='utf-8'))
                else:
                    connections[recevier].send(bytes(envelop, encoding='utf-8'))
                    print(f'-- Send message from "{sender}" to "{recevier}".')


def login(sock):
    name = input('login>')
    sock.send(bytes(f'{name}:server:login', encoding='utf-8'))
    resp = sock.recv(1024).decode()
    print(resp)
    return name


def startchat(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: 
            sock.connect((ip, int(port)))
            sender = login(sock)
            receiver = input('chatwith>')
            while True:
                message = input('>')
                envelope = f'{sender}:{receiver}:{message}'
                sock.send(bytes(envelope, encoding='utf-8'))  
                response = sock.recv(1024).decode()
                print(response)
 

if __name__ == '__main__':
    if argv[1] == 'runserver':
        runserver(argv[2], argv[3]) 
    elif argv[1] == 'startchat':
        startchat(argv[2], argv[3])
        
