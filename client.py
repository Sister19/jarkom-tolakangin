import lib.connection
from lib.segment import Segment
import lib.segment as segment
import random

class Client:
    def __init__(self, host, port, destPort):
        # Init client
        self.host = host
        self.port = port
        self.destPort = destPort
        self.conn = lib.connection.Connection(host,port)
        self.segment = segment.Segment()
        print(f" [!] Client started at {self.host}:{self.port}")

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        # STEP 1: SYN, initiate connection
        self.segment.set_flag([0, 1, 0]) # SYN flag
        seqNum = 100
        self.segment.set_payload(b'test send data')
        self.segment.set_header({
        'seq_num': seqNum,
        'ack_num': 0,
        'flag': self.segment.get_flag(),
        'payload': self.segment.get_payload()
        })

        print("[!] Initiating three way handshake...")

        self.conn.send_data(self.segment, (self.host,self.destPort))

        print(f"[!] [Handshake] Sending broadcast SYN request to port {self.destPort}")
        # print(self.segment)
        print("[!] [Handshake] Waiting for response...")

        data, addr = self.conn.listen_single_segment()
        if data.get_syn() == 1 and data.get_ack() == 1:
            if data.valid_checksum():
                print("[!] [Handshake] SYN-ACK received.")

                # STEP 3: send ACK from client to server
                data.set_flag([0,0,1])
                header = data.get_header()
                serverACK = header['ack_num']
                serverSeq = header['seq_num']
                data.set_header({
                'seq_num': serverACK,
                'ack_num': serverSeq+1,
                })
                print("[!] [Handshake] Connection established. Sending ACK.")
                self.conn.send_data(data, (self.host,self.destPort))
                # print(data)
            else:
                print("[!] [Handhshake] Checksum failed. Connection is terminated.")

    def listen_file_transfer(self):
        # File transfer, client-side
        pass


if __name__ == '__main__':
    main = Client('localhost',50006,50007)
    main.three_way_handshake()
    # main.listen_file_transfer()
