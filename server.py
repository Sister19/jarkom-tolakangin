from typing import Union
import lib.connection
from lib.segment import Segment
import lib.segment as segment
import socket
import random

class Server:
    def __init__(self, host, port):
        # Init server
        self.host = host
        self.port = port
        self.conn = lib.connection.Connection(self.host,self.port)
        self.conn.socket.bind((self.host,self.port))
        self.clients = {}
        print(f"[!] Server started at {self.host}:{self.port}")
        print(f"[!] Source file | unset | x bytes")
        print("[!] Listening to broadcast address for clients.")

    def listen_for_clients(self):
        # Server listening
        listening = True
        while listening:
                data, addr = self.conn.listen_single_segment()
                print(f"[!] Received request from {addr[0]}:{addr[1]}")
                self.clients[addr] = data
                isListenMore = input("Listen more? (y/n)")
                if isListenMore == "n":
                    break
        print("\nClient list:")
        for idx, (key, _val) in enumerate(self.clients.items()):
            print(f"{idx+1}. {key[0]}:{key[1]}")
        print("")

    def start_file_transfer(self):
        # Handshake & file transfer for all client
        for idx, (key, val) in enumerate(self.clients.items()):
            host = key[0]
            port = key[1]
            print("[!] Commencing file transfer...")
            print(f"[!] [Handshake] Handshake to client {idx+1}...")
            self.three_way_handshake((host, port))

    def file_transfer(self, client_addr : Union[str, int]):
        # File transfer, server-side, Send file to 1 client
        pass

    def three_way_handshake(self, client_addr: Union[str, int]) -> bool:
        # Three way handshake, server-side, 1 client

        # STEP 2: SYN-ACK from server to client
        if self.clients[client_addr].get_syn() == 1:
            print(f"[!] [Handshake] Sending SYN-ACK")
            data: Segment = self.clients[client_addr]
            header = data.get_header()
            clientACK = header['seq_num']
            seqNum = random.randint(0,2**32-1)
            data.set_header({
            'seq_num': seqNum,
            'ack_num': clientACK+1,
            })
            data.set_flag([0,1,1])
            # print(data)
            self.conn.send_data(data, client_addr)

            dataEstablished, addr = self.conn.listen_single_segment()
            if dataEstablished.get_ack() == 1:
                print("[!] [Handshake] Connection established.\n")


if __name__ == '__main__':
    main = Server('localhost',50007)
    main.listen_for_clients()
    main.start_file_transfer()
