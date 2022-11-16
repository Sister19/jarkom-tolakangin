import socket
from typing import Dict, Union
from .segment import Segment

class Connection:
    def __init__(self, ip : str, port : int):
        # Init UDP socket
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_data(self, msg : Segment, Tuple : Union[str, int] = None):
        # Send single segment into destination
        self.socket.sendto(msg.get_bytes(), Tuple)

    def listen_single_segment(self) -> Segment:
        # Listen single UDP datagram within timeout and convert into segment
        # 32768 is buffer size
        # self.socket.settimeout(300.0)
        data, addr = self.socket.recvfrom(32768)
        seg = Segment()
        seg.set_from_bytes(data)
        return seg, addr

    def close_socket(self):
        # Release UDP socket
        self.socket.close()