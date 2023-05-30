from typing import Protocol
import psycopg2
import os
import dotenv
from models import Client, Envelope


# Env loading
dotenv_path = '.env'
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)
env = os.environ.get


class ChatStorageProtocol(Protocol):
    def __init__(self) -> None:
        ...
     
    def __del__(self) -> None:
        ...

    def migrate_initial_scheme(self) -> None:
        ... 
    
    def reg_member(self, login, passwd) -> bool:
        ...

    def auth_member(self, login, passwd) -> bool:
        ... 

    def get_members(self, login=None, count=None) -> list:
        ...
    
    def add_envelope(self, envelope: Envelope) -> bool:
        ...

    def get_envelopes(self, sender=None, recevier=None,
                         datetime_order=False, count=None) -> list:
        ...


class ChatPostgresStorage(ChatStorageProtocol):
    def __init__(self) -> None:
            self.conn = psycopg2.connect(
               dbname=env('POSTGRES_DB'),
               password=env('POSTGRES_PASSWORD'),
               user=env('POSTGRES_USER'),
               host=env('DB_HOST'),
               port=env('DB_PORT')
            )
            self.cur = self.conn.cursor()
            self.migrate_initial_scheme()
     
    def __del__(self) -> None:
        self.conn.close()
        self.cur.close()
     
    def migrate_initial_scheme(self) -> None:
        try:
            create_tables = '''
            CREATE TABLE members (
                id     serial primary key,
                login  varchar(255) UNIQUE, 
                passwd varchar(255) 
            );
            CREATE TABLE envelopes (
                id          serial primary key,
                sender_id   int references members (id),
                recevier_id int references members (id),
                date        timestamp,
                message     text,
                is_recv     boolean default false
            );
            '''
            print('Migrate database ... ', end='')
            self.cur.execute(create_tables)
            self.conn.commit()
            print('OK')
        except Exception as _ex:
            self.conn.rollback()
            print('OK')
            print('\n---------------WARNING---------------\n', _ex, 
                    '-------------------------------------', sep='')
    
    def reg_member(self, login, passwd) -> bool:
        try: 
            query = f'''
            INSERT INTO members (login, passwd) 
            VALUES ('{login}', '{passwd}'); 
            '''
            self.cur.execute(query)
            self.conn.commit()
        except Exception as _ex:
            self.conn.rollback()
            print(_ex)
            return False
        return True
    
    def auth_member(self, login, passwd) -> bool:
        member = None 
        try: 
            query = f'''
            SELECT * FROM members
            WHERE login='{login}'
            AND passwd='{passwd}'
            '''
            self.cur.execute(query)
            member = self.cur.fetchone()
        except Exception as _ex:
            self.conn.rollback()
            print(_ex)
            return False
        if member is None:
            return False
        return True
     
    def get_members(self, login=None, count=None) -> list: 
        members = []
        try:
            query = None
            if login is not None:
                query = f'''
                SELECT * FROM members
                WHERE login='{login}'
                ''' 
            elif count is not None:
                query = f'''
                SELECT * FROM members 
                LIMIT {count}
                '''
            else:
                query = f'''
                SELECT * FROM members;
                '''
            self.cur.execute(query)
            items = self.cur.fetchall()
            for item in items:
                members.append(Client(item[0], item[1]))
        except Exception as _ex:
            print(_ex)
        return members
         
    def add_envelope(self, envelope: Envelope) -> bool: 
        try:
            query = f'''
            INSERT INTO envelopes (sender_id, recevier_id, date, message)
            VALUES ('{envelope.sender.id}', '{envelope.recevier.id}', 
                    '{envelope.date}', '{envelope.load}');
            '''
            self.cur.execute(query)
            self.conn.commit()
        except Exception as _ex:
            self.conn.rollback()
            print(_ex)
            return False
        return True
    
    def accept_recv(self, envelope: Envelope) -> None:
        try:
            query = f'''
            UPDATE envelopes SET is_recv = true 
            WHERE sender_id={envelope.sender.id}
            AND recevier_id={envelope.recevier.id} 
            '''
            self.cur.execute(query)
            self.conn.commit()
        except Exception as _ex:
            self.conn.rollback()
            print(_ex)


    def get_envelopes(self, sender: Client, recevier: Client,
                      count=None, is_resv=True) -> list:
        envelopes = []
        try:
            if is_resv:
                if count is None:
                    query = f'''
                    SELECT * FROM envelopes
                    WHERE sender_id={sender.id}
                    AND recevier_id={recevier.id}
                    ORDER BY date
                    '''
                else:
                    query = f'''
                    SELECT * FROM envelopes
                    WHERE sender_id={sender.id}
                    AND recevier_id={recevier.id}
                    ORDER BY date
                    LIMIT {count}
                    '''
            else:
                if count is None:
                    query = f'''
                    SELECT * FROM envelopes
                    WHERE sender_id={sender.id}
                    AND recevier_id={recevier.id}
                    AND is_recv = false
                    ORDER BY date
                    '''
                else:
                    query = f'''
                    SELECT * FROM envelopes
                    WHERE sender_id={sender.id}
                    AND recevier_id={recevier.id}
                    AND is_recv = false
                    ORDER BY date
                    LIMIT {count}
                    '''
            self.cur.execute(query)
            items = self.cur.fetchall()
            for item in items:
                envelopes.append(Envelope(item[1], item[2], item[3], item[4]))
        except Exception as _ex:
            print(_ex)
        return envelopes 
