import struct

from .constant import (ACK_FLAG, EXTENSION_END, EXTENSION_MAX_SIZE,
                       EXTENSION_START, FILENAME_END, FILENAME_MAX_SIZE,
                       FILENAME_START, FIN_FLAG, PAYLOAD_END, PAYLOAD_MAX_SIZE,
                       PAYLOAD_START, SYN_FLAG)


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
    # 12-32767 : payload (32756 bytes)
    # 32768-33023   : metadata filename (256 bytes)
    # 33024-33027   : metadata extension (4 bytes)
    # TOTAL: 33028 bytes

    # -- Internal Function --
    def __init__(self):
        # Initalize segment with default value
        self.seq_num = 0b0
        self.ack_num = 0b0
        self.flag = SegmentFlag(0b0)
        self.payload = b''
        self.checksum = 0b0
        self.metadata_filename = b''
        self.metadata_extension = b''

    def __str__(self):
        output = "{\n"
        output += f'\tseq_num: {self.seq_num}\n'
        output += f'\tack_num: {self.ack_num}\n'
        output += f'\tflag: {self.flag}\n'
        output += f'\tchecksum: {self.checksum}\n'
        output += f'\tpayload: {self.payload}\n'
        output += f'\tfilename: {self.metadata_filename}\n'
        output += f'\textension: {self.metadata_extension}\n'
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
                sums = (sums + struct.unpack('>H',
                        self.payload[i:i+2])[0]) & 0xFF
            else:
                sums = (sums + struct.unpack('>B',
                        self.payload[i:i+1])[0]) & 0xFF
        # jumlahkan metadata filename
        for i in range(0, len(self.metadata_filename), 2):
            if i + 1 < len(self.metadata_filename):
                sums = (sums + struct.unpack('>H',
                        self.metadata_filename[i:i+2])[0]) & 0xFF
            else:
                sums = (sums + struct.unpack('>B',
                        self.metadata_filename[i:i+1])[0]) & 0xFF
        # jumlahkan metadata extension
        for i in range(0, len(self.metadata_extension), 2):
            if i + 1 < len(self.metadata_extension):
                sums = (sums + struct.unpack('>H',
                        self.metadata_extension[i:i+2])[0]) & 0xFF
            else:
                sums = (sums + struct.unpack('>B',
                        self.metadata_extension[i:i+1])[0]) & 0xFF
        # kembalikan hasil
        return ~sums & 0xFF

    # -- Setter --

    def set_header(self, header: dict):
        # header = {
        #   'seq_num': int,
        #   'ack_num': int,
        #   'flag': SegmentFlag,
        #   'payload': bytes
        #   'filename': bytes
        #   'extension': bytes
        # }
        if ('seq_num' in header.keys()):
            self.seq_num = header['seq_num']
        if ('ack_num' in header.keys()):
            self.ack_num = header['ack_num']
        if ('flag' in header.keys()):
            self.flag = header['flag']
        if ('payload' in header.keys()):
            self.payload = header['payload']
        if ('filename' in header.keys()):
            self.metadata_filename = header['filename']
        if ('extension' in header.keys()):
            self.metadata_extension = header['extension']
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

    def set_syn(self, syn: bool):
        self.flag.syn = syn
        self.checksum = self.__calculate_checksum()

    def set_ack(self, ack: bool):
        self.flag.ack = ack
        self.checksum = self.__calculate_checksum()

    def set_fin(self, fin: bool):
        self.flag.fin = fin
        self.checksum = self.__calculate_checksum()

    def set_metadata_filename(self, filename: bytes):
        self.metadata_filename = filename
        self.checksum = self.__calculate_checksum()

    def set_metadata_extension(self, ext: bytes):
        self.metadata_extension = ext
        self.checksum = self.__calculate_checksum()

    # -- Getter --

    def get_header(self) -> dict:
        return {
            'seq_num': self.seq_num,
            'ack_num': self.ack_num,
            'flag': self.flag,
            'checksum': self.checksum,
            'payload': self.payload,
            'filename': self.metadata_filename,
            'extension': self.metadata_extension
        }

    def get_payload(self) -> bytes:
        return bytes(self.payload)

    def get_flag(self) -> SegmentFlag:
        return self.flag

    def get_syn(self) -> bool:
        return self.flag.syn

    def get_ack(self) -> bool:
        return self.flag.ack

    def get_fin(self) -> bool:
        return self.flag.fin

    def get_metadata_filename(self) -> bytes:
        return self.metadata_filename

    def get_metadata_extension(self) -> bytes:
        return self.metadata_extension

    # -- Marshalling --

    def set_from_bytes(self, src: bytes):
        # From pure bytes, unpack() and set into python variable
        # asumsi src adalah bytes yang valid termasuk checksumnya
        temp = struct.unpack('!IIBBH', src[:12])
        self.seq_num = temp[0]
        self.ack_num = temp[1]
        self.flag = SegmentFlag(temp[2])
        self.checksum = temp[4]
        self.payload = src[PAYLOAD_START:src.find(b'\x00', PAYLOAD_START)]
        self.metadata_filename = src[FILENAME_START:src.find(
            b'\x00', FILENAME_START)]
        self.metadata_extension = src[EXTENSION_START:]

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        return struct.pack('!IIBBH',
                           self.seq_num,
                           self.ack_num,
                           self.flag.get_flag_bytes(), 0b0, self.checksum
                        #    self.payload +
                        #    (b'\x00' * (PAYLOAD_MAX_SIZE - len(self.payload))),
                        #    self.metadata_filename +
                        #    (b'\x00' * (FILENAME_MAX_SIZE -
                        #     len(self.metadata_filename))),
                        #    self.metadata_extension +
                        #    (b'\x00' * (EXTENSION_MAX_SIZE -
                        #     len(self.metadata_extension)))
                        #    )
           ) + self.payload + (b'\x00' * (PAYLOAD_MAX_SIZE - len(self.payload))) + self.metadata_filename + (b'\x00' * (FILENAME_MAX_SIZE - len(self.metadata_filename))) + self.metadata_extension

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

    # sampleseg.set_payload(b'test payload keren banget')
    # print(sampleseg.get_payload())
    # print(sampleseg.valid_checksum())

    sampleseg.set_metadata_filename(b'hehehe')
    print(sampleseg.get_metadata_filename())
    print(sampleseg.valid_checksum())

    sampleseg.set_metadata_extension(b'jpeg')
    print(sampleseg.get_metadata_extension())
    print(sampleseg.valid_checksum())

    print(sampleseg)

    # sampleseg.payload = b'test payload nahloh ganti paksa'
    # print(sampleseg.get_payload())
    # print(sampleseg.valid_checksum())

    # print(sampleseg)
