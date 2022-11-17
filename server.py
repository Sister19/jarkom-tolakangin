from typing import Union
import lib.connection
import lib.constant
import lib.segment
import math
import argparse
import os

class Server:
    def __init__(self, host, port, filepath):
        # Init server
        self.host = host
        self.port = port
        self.conn = lib.connection.Connection(self.host,self.port)
        self.conn.socket.bind((self.host,self.port))
        self.clients = {}
        self.filepath = filepath
        self.filesize = os.path.getsize(self.filepath)
        self.windowSize = lib.constant.WINDOW_SIZE
        self.buffersize = self.filesize
        self.readOffset = 0
        print(f"[!] Server started at {self.host}:{self.port}")
        print(f"[!] Source file | {self.filepath} | {self.filesize} bytes")
        print("[!] Listening to broadcast address for clients.")
        # print(self.payload)

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
        file = open(self.filepath, "rb")
        windowSize = self.windowSize
        sequenceBase = 0
        sequenceMax = int(windowSize) + 1
        maxSegment = math.ceil(self.filesize / lib.constant.MAX_DATA_SIZE)
        goBackN = False
        error = False

        # Loop until all segments are sent
        while sequenceBase < maxSegment:
            # Loop until window is full
            sequenceNum = int(sequenceBase) + 1
            repeatCount = 0
            while sequenceNum < min(maxSegment+1, sequenceMax):
                try:
                    data: lib.segment.Segment = self.clients[client_addr]
                    if (sequenceNum != maxSegment):
                        data.set_flag([0,0,0])
                        file.seek((sequenceNum-1)*lib.constant.MAX_DATA_SIZE)
                        data.set_payload(file.read(lib.constant.MAX_DATA_SIZE))
                        data.set_header({
                            "seq_num": sequenceNum-1,
                        })
                        self.conn.send_data(data, client_addr)
                        print(f"[Segment SEQ={sequenceNum}] Sent to {client_addr[0]}:{client_addr[1]}")
                        sequenceNum += 1
                        repeatCount = 0
                    else: # Last segment
                        data.set_flag([1,0,0])
                        file.seek((sequenceNum-1)*lib.constant.MAX_DATA_SIZE)
                        data.set_payload(file.read(lib.constant.MAX_DATA_SIZE))
                        data.set_header({
                            "seq_num": sequenceNum-1,
                        })
                        self.conn.send_data(data, client_addr)
                        print(f"[Segment SEQ={sequenceNum}] Sent to {client_addr[0]}:{client_addr[1]}")
                        sequenceNum += 1
                        repeatCount = 0
                except self.conn.socket.timeout:
                    print(f"[!] [Segment SEQ={sequenceNum}] Timeout, resending...")
                    repeatCount += 1
                    if repeatCount == lib.constant.MAX_REPEAT:
                        error = True
                        break

            # Wait for ACK
            for i in range(int(sequenceBase)+1, int(sequenceNum)):
                rcvSeg, addr = self.conn.listen_single_segment()
                requestNum = int(rcvSeg.get_header()['ack_num'])

                # If ACK is valid
                if (requestNum > sequenceBase and addr[1] == client_addr[1]):
                    sequenceMax = int(sequenceMax) - int(sequenceBase) + int(requestNum)
                    sequenceBase = int(requestNum)
                    print(f"[Segment SEQ={i}] Acked")
                # If ACK is invalid
                elif (addr[1] != client_addr[1]):
                    goBackN = True
                    print(f"[Segment SEQ={i}] Not Acked. Wrong client.")
                    print(f"Commencing Go-Back-N protocol from Segment SEQ={i} to {client_addr[0]}:{client_addr[1]}")
                    break
                else:
                    goBackN = True
                    print(f"[Segment SEQ={i}] Not Acked. Duplicate ACK found.")
                    print(f"Commencing Go-Back-N protocol from Segment SEQ={i} to {client_addr[0]}:{client_addr[1]}")
                    break
        
        if goBackN:
            print("[!] Go-Back-N protocol success")
        if (not error):
            print("[!] File transfer completed\n")

        file.close()
        self.close_connection(client_addr)

    def close_connection(self, client_addr : Union[str, int]):
        # Close connection, server-side
        print("[!] Closing connection...")
        
        rcvFIN, addr = self.conn.listen_single_segment()
        if (rcvFIN.get_fin() and addr[1] == client_addr[1]):
            print(f"[!] Received FIN from {addr[0]}:{addr[1]}")
            tw1 = lib.segment.Segment()
            tw1.set_flag([0,0,1])
            self.conn.send_data(tw1, client_addr)
            print(f"[!] Sending ACK to {client_addr[0]}:{client_addr[1]}")

        tw2 = lib.segment.Segment()
        tw2.set_flag([1,0,0])
        print(f"[!] Sending FIN to {client_addr[0]}:{client_addr[1]}")
        self.conn.send_data(tw2, client_addr)

        rcvACK, addr = self.conn.listen_single_segment()
        if (rcvACK.get_ack() and addr[1] == client_addr[1]):
            print(f"[!] Received ACK from {addr[0]}:{addr[1]}")
            print(f"[!] Connection closed with {client_addr[0]}:{client_addr[1]}\n")
        
        # if this is the last client, close the server socket
        if list(self.clients).index(client_addr) == len(self.clients)-1:
            self.conn.close_socket()

    def three_way_handshake(self, client_addr: Union[str, int]) -> bool:
        # Three way handshake, server-side, 1 client

        # STEP 2: SYN-ACK from server to client
        data: lib.segment.Segment = self.clients[client_addr]
        if data.get_syn():
            if data.valid_checksum():
                header = data.get_header()
                clientACK = header['seq_num']
                data.set_flag([0,1,1])
                data.set_header({
                'seq_num': 0,
                'ack_num': clientACK+1,
                })
                # data.set_metadata_filename(bytes(self.filepath.split("/")[-1].split(".")[0], "utf-8"))
                # data.set_metadata_extension(bytes(self.filepath.split(".")[-1], "utf-8"))
                print(data)
                self.conn.send_data(data, client_addr)
                print(f"[!] [Handshake] Sending SYN-ACK")

                # try:
                data, addr = self.conn.listen_single_segment()
                if data.get_ack():
                    if data.valid_checksum():
                        print("[!] [Handshake] Connection established.\n")
                        self.clients[client_addr] = data
                        self.buffersize = self.filesize
                        self.readOffset = 0
                        self.file_transfer(client_addr)
                    else:
                        print("[!] [Handhshake] Checksum failed. Connection is terminated.")
                # except self.conn.socket.timeout:
                #     print("[!] [Handshake] Connection timeout. Connection is terminated.")
            else:
                print("[!] [Handshake] Checksum failed. Connection is terminated.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("inputPath", type=str)
    args = parser.parse_args()

    main = Server('localhost', args.port, args.inputPath)
    
    main.listen_for_clients()
    main.start_file_transfer()
