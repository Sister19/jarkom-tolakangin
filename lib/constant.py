# flag constants
SYN_FLAG = 0b10     # pada bit ke-1
ACK_FLAG = 0b10000  # pada bit ke-4
FIN_FLAG = 0b1      # pada bit ke-0

# segment sizes
PAYLOAD_START = 12
PAYLOAD_END = 32767
PAYLOAD_MAX_SIZE = 32756

FILENAME_START = 32768
FILENAME_END = 33023
FILENAME_MAX_SIZE = 256

EXTENSION_START = 33024
EXTENSION_END =33027
EXTENSION_MAX_SIZE = 4

WINDOW_SIZE = 4

MAX_DATA_SIZE = 32756	# before metadata
# MAX_DATA_SIZE = 33028	# after metadata
