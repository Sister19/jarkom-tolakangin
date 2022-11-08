import struct

# Constants
SYN_FLAG = 0b10     # pada bit ke-1
ACK_FLAG = 0b10000  # pada bit ke-4
FIN_FLAG = 0b1      # pada bit ke-0


class SegmentFlag:
    # flag_bytes: unsigned char
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
        return f'byte={bin(self.flag_bytes)};FIN={self.fin};SYN={self.syn};ACK={self.ack}'

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        return self.flag_bytes


class Segment:
    # SEGMENT FORMAT
    # 0-3     : seq (4 bytes, unsigned int)
    # 4-7     : ack (4 bytes, unsigned int)
    # 8       : flag (1 byte, unsigned char)
    # 9       : kosong (1 byte, unsigned char)
    # 10-11   : checksum (2 bytes, unsigned short)
    # 12-3767 : data (3756 bytes)

    # -- Internal Function --
    def __init__(self):
        # Initalize segment with default value
        self.seq_num = 0b0
        self.ack_num = 0b0
        self.flag = SegmentFlag(0b0)
        self.checksum = 0b0
        self.data = b''

    def __str__(self):
        output = ""
        output += f'seq_num: {self.seq_num}\n'
        output += f'ack_num: {self.ack_num}\n'
        output += f'flag: {self.flag}\n'
        output += f'checksum: {self.checksum}\n'
        output += f'data: {self.data}\n'
        return output

    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        # kalkulasi menggunakan CRC polinomial
        pass

    # -- Setter --

    def set_header(self, header: dict):
        # header = {
        #   'seq_num': int,
        #   'ack_num': int,
        #   'flag': SegmentFlag,
        #   'checksum': int,
        #   'data': bytes
        # }
        self.seq_num = header['seq_num']
        self.ack_num = header['ack_num']
        self.flag = header['flag']
        self.checksum = header['checksum']
        self.data = header['data']

    def set_payload(self, payload: bytes):
        # ambil data dari payload
        self.data = payload

    def set_flag(self, flag_list: list):
        # asumsi flag_list = [fin: bool, syn: bool, ack: bool]
        self.flag = SegmentFlag(flag_list[0] | flag_list[1] << 1 | flag_list[2] << 4)

    # -- Getter --

    def get_flag(self) -> SegmentFlag:
        return self.flag

    def get_header(self) -> dict:
        return {
            'seq_num': self.seq_num,
            'ack_num': self.ack_num,
            'flag': self.flag,
            'checksum': self.checksum,
            'data': self.data
        }

    def get_payload(self) -> bytes:
        return self.data

    # -- Marshalling --

    def set_from_bytes(self, src: bytes):
        # From pure bytes, unpack() and set into python variable
        temp = struct.unpack('IIBBH', src)
        self.seq_num = temp[0]
        self.ack_num = temp[1]
        self.flag = SegmentFlag(temp[2])
        self.checksum = temp[4]
        self.data = src[12:]
        pass

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        return struct.pack('IIBBH',
                            self.seq_num,
                            self.ack_num,
                            self.flag.get_flag_bytes(), 0b0, self.checksum) + self.data

    # -- Checksum --

    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        pass


if __name__ == "__main__":
    print("segment.py demo")
    # print(SegmentFlag(0b10010))
    sampleseg = Segment()
    sampleseg.set_flag([1, 0, 1])
    sampleseg.set_payload('hello')
    sampleseg.set_header({
        'seq_num': 1,
        'ack_num': 2,
        'flag': sampleseg.get_flag(),
        'checksum': 0,
        'data': sampleseg.get_payload()
    })
    print(sampleseg)
    pass
