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

        data, addr = self.conn.listen_single_segment()
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
                print("[!] [Handhshake] Checksum failed. Connection is terminated.")

    def listen_file_transfer(self):
        # File transfer, client-side
        requestNum = 0
        file = open(self.outputPath, "ab", newline=None)
        error = False

        while True:
            rcvSeg, addr = self.conn.listen_single_segment()
            sequenceNum = int(rcvSeg.get_header()['seq_num'])
            if (sequenceNum == requestNum):
                requestNum = sequenceNum + 1
                if (not rcvSeg.get_fin()):
                    file.write(rcvSeg.get_payload())
                    seg = segment.Segment()
                    seg.set_flag([0,0,1])
                    seg.set_header({
                        'seq_num': sequenceNum,
                        'ack_num': requestNum,
                    })
                    self.conn.send_data(seg, (self.host,self.destPort))
                    print(f"[Segment SEQ={sequenceNum+1}] received. Ack sent to {self.host}:{self.destPort}")
                else: # FIN flag
                    file.write(rcvSeg.get_payload())
                    seg = segment.Segment()
                    seg.set_flag([1,0,1])
                    seg.set_header({
                        'seq_num': sequenceNum,
                        'ack_num': requestNum,
                    })
                    self.conn.send_data(seg, (self.host,self.destPort))
                    print(f"[Segment SEQ={sequenceNum+1}] received. Ack sent to {self.host}:{self.destPort}")
                    break
            else:
                errSeg = segment.Segment()
                errSeg.set_flag([0,0,0])
                errSeg.set_header({
                    'ack_num': requestNum,
                })
                error = True
                self.conn.send_data(errSeg, (self.host,self.destPort))
                print(f"[Segment SEQ={sequenceNum+1}] damaged. Ack {sequenceNum} sent to {self.host}:{self.destPort}")
        
        if (error):
            print("[!] Go-Back-N protocol success.")
        print("[!] File transfer completed.")
        
        file.close()
        self.close_connection()
        
        # if not(data.get_syn()) and not(data.get_ack()) and not(data.get_fin()):
        #     header = data.get_header()
        #     serverACK = header['ack_num']
        #     serverSeq = header['seq_num']
        #     data.set_header({
        #     'seq_num': serverACK,
        #     'ack_num': serverSeq+1,
        #     })
        #     data.set_flag([0,0,1])
        #     print(f"[Segment SEQ={serverSeq}] Received, Ack sent")
        #     self.conn.send_data(data, (self.host,self.destPort))
        # with open(self.outputPath, 'wb') as f:
        #     f.write(data.get_payload())

    def close_connection(self):
        # Close connection, client-side
        print("[!] Closing connection...")
        fw = segment.Segment()
        fw.set_flag([1,0,1])
        print("Sending FIN to server...")
        
        self.conn.send_data(fw, (self.host,self.destPort))
        print("Waiting for server response...")
        self.conn.listen_single_segment()
        print("Received ACK from server")
        self.conn.listen_single_segment()
        print("Received FIN-ACK from server")

        fw3 = segment.Segment()
        fw3.set_flag([0,0,1])
        print("Sending ACK to server...")
        self.conn.send_data(fw3, (self.host,self.destPort))
        print(f"[!] Connection closed with {self.host}:{self.destPort}")


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
