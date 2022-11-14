from typing import Tuple
import lib.connection
from lib.segment import Segment
import lib.segment as segment
import socket

class Server:
    def __init__(self, host, port):
        # Init server
        self.host = host
        self.port = port
        self.conn = lib.connection.Connection(self.host,self.port)
        self.conn.socket.bind((self.host,self.port))
        print(f"[!] Server started at {self.host}:{self.port}")

    def listen_for_clients(self):
        # Server listening
        listening = True
        while listening:
            print(self.conn.listen_single_segment())

    def start_file_transfer(self):
        # Handshake & file transfer for all client
        pass

    def file_transfer(self, client_addr : Tuple["ip", "port"]):
        # File transfer, server-side, Send file to 1 client
        pass

    def three_way_handshake(self, client_addr: Tuple["ip", "port"]) -> bool:
       # Three way handshake, server-side, 1 client
       pass


if __name__ == '__main__':
    main = Server('localhost',50007)
    main.listen_for_clients()
    # main.start_file_transfer()
