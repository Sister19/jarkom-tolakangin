import lib.connection
from lib.segment import Segment
import lib.segment as segment

class Client:
    def __init__(self, host, port):
        # Init client
        self.host = host
        self.port = port
        self.conn = lib.connection.Connection(host,port)
        self.segment = segment.Segment()
        self.segment.set_payload(b'test send data')
        self.segment.set_flag([1, 0, 0])

        print("Sending data...")
        print(self.segment)
        self.conn.send_data(self.segment, (host, port))

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        pass

    def listen_file_transfer(self):
        # File transfer, client-side
        pass


if __name__ == '__main__':
    main = Client('localhost',50007)
    # main.three_way_handshake()
    # main.listen_file_transfer()
