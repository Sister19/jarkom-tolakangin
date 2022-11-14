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

    def isSyn(self) -> bool:
        return 


class Segment:
    # SEGMENT FORMAT
    # 0-3     : seq (4 bytes, unsigned int)
    # 4-7     : ack (4 bytes, unsigned int)
    # 8       : flag (1 byte, unsigned char)
    # 9       : kosong (1 byte, unsigned char)
    # 10-11   : checksum (2 bytes, unsigned short)
    # 12-3767 : payload (32756 bytes)

    # -- Internal Function --
    def __init__(self):
        # Initalize segment with default value
        self.seq_num = 0b0
        self.ack_num = 0b0
        self.flag = SegmentFlag(0b0)
        self.payload = b''
        self.checksum = self.__calculate_checksum()

    def __str__(self):
        output = "{"
        output += f'\tseq_num: {self.seq_num}\n'
        output += f'\tack_num: {self.ack_num}\n'
        output += f'\tflag: {self.flag}\n'
        output += f'\tchecksum: {self.checksum}\n'
        output += f'\tpayload: {self.payload}\n'
        output += "}"
        return output

    # def __calculate_checksum(self) -> bytes:
    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        # kalkulasi checksum menggunakan 16-bit 1's complement.
        # tambah 2 byte pertama dan 2 byte terakhir seq_num
        sums = ((self.seq_num & 0xFF) + (self.seq_num >> 16)) & 0xFF
        # tambah 2 byte pertama dan 2 byte terakhir ack_num
        sums = (sums + (self.ack_num & 0xFF) + (self.ack_num >> 16)) & 0xFF
        # tambah flag
        sums = (sums + self.flag.get_flag_bytes()) & 0xFF
        # jumlahkan data per 2 byte payload
        for i in range(0, len(self.payload), 2):
            if i + 1 < len(self.payload):
                sums = (sums + struct.unpack('H', self.payload[i:i+2])[0]) & 0xFF
            else:
                sums = (sums + struct.unpack('B', self.payload[i:i+1])[0]) & 0xFF
        # kembalikan hasil
        return ~sums & 0xFF

    # -- Setter --

    def set_header(self, header: dict):
        # header = {
        #   'seq_num': int,
        #   'ack_num': int,
        #   'flag': SegmentFlag,
        #   'payload': bytes
        # }
        if ('seq_num' in header.keys()):
            self.seq_num = header['seq_num']
        if ('ack_num' in header.keys()):
            self.ack_num = header['ack_num']
        if ('flag' in header.keys()):
            self.flag = header['flag']
        if ('payload' in header.keys()):
            self.payload = header['payload']
        self.checksum = self.__calculate_checksum()

    def set_payload(self, payload: bytes):
        # ambil data dari payload
        self.payload = payload
        self.checksum = self.__calculate_checksum()

    def set_flag(self, flag_list: list):
        # asumsi flag_list = [fin: bool, syn: bool, ack: bool]
        self.flag = SegmentFlag(
            flag_list[0] | flag_list[1] << 1 | flag_list[2] << 4)
        self.checksum = self.__calculate_checksum()

    # -- Getter --

    def get_flag(self) -> SegmentFlag:
        return self.flag

    def get_header(self) -> dict:
        return {
            'seq_num': self.seq_num,
            'ack_num': self.ack_num,
            'flag': self.flag,
            'checksum': self.checksum,
            'payload': self.payload
        }

    def get_payload(self) -> bytes:
        return bytes(self.payload)

    # -- Marshalling --

    def set_from_bytes(self, src: bytes):
        # From pure bytes, unpack() and set into python variable
        # asumsi src adalah bytes yang valid termasuk checksumnya
        temp = struct.unpack('IIBBH', src[:12])
        self.seq_num = temp[0]
        self.ack_num = temp[1]
        self.flag = SegmentFlag(temp[2])
        self.checksum = temp[4]
        self.payload = src[12:]

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        return struct.pack('IIBBH',
                           self.seq_num,
                           self.ack_num,
                           self.flag.get_flag_bytes(), 0b0, self.checksum) + self.payload

    # -- Checksum --

    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        return self.__calculate_checksum() == self.checksum


if __name__ == "__main__":
    sampleseg = Segment()

    sampleseg.set_flag([1, 0, 1])
    print(sampleseg.get_flag())
    print(sampleseg.valid_checksum())

    sampleseg.set_header({
        'seq_num': 1,
        'ack_num': 2,
        'flag': sampleseg.get_flag(),
        'checksum': 0,
        'payload': sampleseg.get_payload()
    })
    print('get_header', sampleseg.get_header())
    print('valid checksum', sampleseg.valid_checksum())

    sampleseg.set_payload(b'test payload keren banget')
    print(sampleseg.get_payload())
    print(sampleseg.valid_checksum())

    sampleseg.payload = b'test payload nahloh ganti paksa'
    print(sampleseg.get_payload())
    print(sampleseg.valid_checksum())
