from lib.connection import Connection
from lib.segment import Segment

s = Connection('127.0.0.1', 1254)

x = Segment()
x.set_payload(b'test send data')
x.set_flag([1, 0, 0])

print("Sending data...")
print(x)
s.send_data(x, ('127.0.0.1', 1254))