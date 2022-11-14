from typing import Tuple
import lib.connection
from lib.segment import Segment
import lib.segment as segment
import socket
import time

class Server:
    def __init__(self, host, port):
        # Init server
        self.host = host
        self.port = port
        self.conn = lib.connection.Connection(self.host,self.port)
        self.conn.socket.bind((self.host,self.port))
        print(f"[!] Server started at {self.host}:{self.port}")
        print(f"[!] Source file | unset | x bytes")
        print("[!] Listening to broadcast address for clients.")

    def listen_for_clients(self):
        # Server listening
        listening = True
        clientList = []
        while listening:
            try:
                receivedSeg, addr = self.conn.listen_single_segment()
                print(f"[!] Received request from {addr[0]}:{addr[1]}")
                clientList.append(addr)
                isListenMore = input("Listen more? (y/n)")
                if isListenMore == "n":
                    break
            except socket.error as e:
                break
        print("\nClient list:")
        for idx, val in enumerate(clientList):
            print(f"{idx+1}. {val[0]}:{val[1]}")

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
