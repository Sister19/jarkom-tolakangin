import lib.connection
import lib.segment as segment
import argparse
import os

class Client:
    def __init__(self, host, port, destPort, outputPath):
        # Init client
        self.host = host
        self.port = port
        self.destPort = destPort
        self.conn = lib.connection.Connection(host,port)
        self.segment = segment.Segment()
        self.outputPath = outputPath
        self.payload = None
        print(f"[!] Client started at {self.host}:{self.port}")

    def three_way_handshake(self):
        # Three Way Handshake, client-side

        # STEP 1: SYN, initiate connection
        print("[!] Initiating three way handshake...")
        self.segment.set_flag([0, 1, 0]) # SYN flag
        seqNum = 0
        self.segment.set_header({
        'seq_num': seqNum,
        'ack_num': 0
        })
        self.conn.send_data(self.segment, (self.host,self.destPort))
        print(f"[!] [Handshake] Sending broadcast SYN request to port {self.destPort}")

        # print(self.segment)
        print("[!] [Handshake] Waiting for response...")

        try:
            data, addr = self.conn.listen_single_segment()
            print(data)
            if data.get_syn() and data.get_ack():
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
                    self.conn.send_data(data, (self.host,self.destPort))
                    print("[!] [Handshake] Connection established. Sending ACK.")
                    # print(data)
                else:
                    print("[!] [Handshake] Checksum failed. Connection is terminated.")
        except self.conn.socket.timeout:
            print("[!] [Handshake] Timeout. Connection is terminated.")

    def listen_file_transfer(self):
        # File transfer, client-side
        requestNum = 0
        file = open(self.outputPath, "ab", newline=None)
        error = False

        while True:
            seg, addr = self.conn.listen_single_segment()
            sequenceNum = int(seg.get_header()['seq_num'])
            if (seg.valid_checksum()):
                if (sequenceNum == requestNum):
                    requestNum = sequenceNum + 1
                    if (not seg.get_fin()):
                        file.write(seg.get_payload())
                        seg.set_flag([0,0,1])
                        seg.set_header({
                            'seq_num': sequenceNum,
                            'ack_num': requestNum,
                        })
                        self.conn.send_data(seg, (self.host,self.destPort))
                        print(f"[Segment SEQ={sequenceNum+1}] received. Ack sent to {self.host}:{self.destPort}")
                    else: # FIN flag
                        file.write(seg.get_payload())
                        seg.set_flag([1,0,1])
                        seg.set_header({
                            'seq_num': sequenceNum,
                            'ack_num': requestNum,
                        })
                        self.conn.send_data(seg, (self.host,self.destPort))
                        print(f"[Segment SEQ={sequenceNum+1}] received. Ack sent to {self.host}:{self.destPort}")
                        break
                else:
                    seg.set_flag([0,0,0])
                    seg.set_header({
                        'ack_num': requestNum,
                    })
                    error = True
                    self.conn.send_data(seg, (self.host,self.destPort))
                    print(f"[Segment SEQ={sequenceNum+1}] damaged. Ack prev SEQ sent to {self.host}:{self.destPort}")
            else:
                print(f"[Segment SEQ={sequenceNum+1}] checksum failed. Connection is terminated.")
                break
        
        if (error):
            print("[!] Go-Back-N protocol success.")
        print("[!] File transfer completed.\n")
        
        file.close()
        self.close_connection()

    def close_connection(self):
        # Close connection, client-side
        print("[!] Closing connection...")
        
        fin = segment.Segment()
        fin.set_flag([1,0,0])
        print("[!] Sending FIN to server...")
        self.conn.send_data(fin, (self.host,self.destPort))

        print("[!] Waiting for server response...")
        fw1, addr = self.conn.listen_single_segment()
        if fw1.get_ack():
            print("[!] Received ACK from server")

        fw2, addr = self.conn.listen_single_segment()
        if fw2.get_fin():
            print("[!] Received FIN from server")

        tw = segment.Segment()
        tw.set_flag([0,0,1])
        print("[!] Sending ACK to server...")
        self.conn.send_data(tw, (self.host,self.destPort))
        print("[!] Connection closed with server")

        # close client socket
        self.conn.close_socket()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("clientPort", type=int)
    parser.add_argument("broadcastPort", type=int)
    parser.add_argument("outputPath", type=str)
    args = parser.parse_args()

    # Delete if previous file exist
    try:
        os.remove(args.outputPath)
    except OSError:
        pass

    main = Client('localhost', args.clientPort, args.broadcastPort, args.outputPath)
    
    main.three_way_handshake()
    main.listen_file_transfer()
