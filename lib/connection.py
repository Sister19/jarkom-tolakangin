import socket
from typing import Dict, Union
from .segment import Segment
from .constant import TOTAL_SEGMENT_SIZE

class Connection:
    def __init__(self, ip : str, port : int):
        # Init UDP socket
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(30)

    def send_data(self, msg : Segment, Tuple : Union[str, int] = None):
        # Send single segment into destination
        self.socket.sendto(msg.get_bytes(), Tuple)

    def listen_single_segment(self) -> Segment:
        # Listen single UDP datagram within timeout and convert into segment
        # 32768 is buffer size
        data, addr = self.socket.recvfrom(TOTAL_SEGMENT_SIZE)
        seg = Segment()
        seg.set_from_bytes(data)
        return seg, addr

    def close_socket(self):
        # Release UDP socket
        self.socket.close()