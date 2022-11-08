from lib.connection import Connection

s = Connection('127.0.0.1', 1254)
s.socket.bind(('127.0.0.1', 1254))

print("Listening...")

while True:
	print(s.listen_single_segment())