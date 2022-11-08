import struct

# Constants
SYN_FLAG = 0b10     # pada bit ke-1
ACK_FLAG = 0b10000  # pada bit ke-4
FIN_FLAG = 0b1      # pada bit ke-0


class SegmentFlag:
    # flag_bytes: bytes
    # syn       : bool (1 bit)
    # ack       : bool (1 bit)
    # fin       : bool (1 bit)

    def __init__(self, flag: bytes):
        # Init flag variable from flag byte
        self.flag_bytes = flag

        # cek FIN di bit ke-0
        self.fin = flag & FIN_FLAG
        # cek SYN di bit ke-1
        self.syn = (flag & SYN_FLAG) >> 1
        # cek ACK di bit ke-4
        self.ack = (flag & ACK_FLAG) >> 4

    def __str__(self):
        return f"bytes: {bin(self.flag_bytes)}\nFIN: {self.fin}\nSYN: {self.syn}\nACK: {self.ack}"

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        return self.flag_bytes


class Segment:
    # SEGMENT FORMAT
    # 0-8: seq (4 bytes). index awal 0
    # 4-7: ack (4 bytes)
    # 8: flag (1 byte)
    # 10-11: checksum (2 bytes)
    # 12-dst: data (bbrp bytes)

    # -- Internal Function --
    def __init__(self):
        # Initalize segment
        self.seq = 0
        self.ack = 0
        self.flag = SegmentFlag(0b0)
        self.data = b''
        pass

    def __str__(self):
        # Optional, override this method for easier print(segmentA)
        output = ""
        output += f"{'Sequence number':24} | {self.sequence}\n"
        return output

    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        pass

    # -- Setter --

    def set_header(self, header: dict):
        pass

    def set_payload(self, payload: bytes):
        pass

    def set_flag(self, flag_list: list):
        pass

    # -- Getter --

    def get_flag(self) -> SegmentFlag:
        pass

    def get_header(self) -> dict:
        pass

    def get_payload(self) -> bytes:
        pass

    # -- Marshalling --

    def set_from_bytes(self, src: bytes):
        # From pure bytes, unpack() and set into python variable
        pass

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        pass

    # -- Checksum --

    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        pass


if __name__ == "__main__":
    print("segment.py demo")
    print(SegmentFlag(0b10010))
    pass
