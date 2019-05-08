#!/Users/nbd712/.pyenv/versions/3.7.0/bin/python3

import socket, os, time, sys, pysnooper, random

os.system("clear")

#@pysnooper.snoop("/Users/nbd712/output.log")
def main():
	HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
	PORT = 65432		# Port to listen on (non-privileged ports are > 1023)
	count = 0

	dotA = [
		b'.AV001,001V002,002V003,003V004,004V005,005V006,006V007,007V008,008',
		b'.AV009,009V010,019V011,011V012,012V013,013V014,014V015,015V016,016',
		b'.AV017,017V018,018V019,003V020,020V021,021V022,022V023,023V024,024',
		b'.AV025,025V026,026V027,027V028,028V029,029V030,030V031,031V032,032',
		b'.AV033,033V034,034V035,035V036,036V037,037V038,038V039,039V040,040',
		b'.AV041,041V042,042V043,043V044,044V045,045V046,046V047,047V048,048',
		b'.AV049,049V050,050V051,051V052,052V053,053V054,054V055,055V056,056',
		b'.AV057,057V058,058V059,059V060,060V061,061V062,062V063,063V064,064',
		]

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((HOST, int(sys.argv[1])))
		s.listen()
		conn, addr = s.accept()
		with conn:
			print('Connected by', addr)
			while True:
				data = conn.recv(1024)
				if not data:
					pass
				elif data[0:2].decode('utf-8') == ".L":
					#return in .A{level}{dest},{srce}{level}{dest},{srce}
					send = dotA[count]
					conn.sendall(send)
					count += 1
					print("Received: {}".format(data))
					print("Sending: {}".format(send))
				elif data[0:3].decode('utf-8') == ".RS":
					#return in .RA[D/S/L]{mnemonic string}(cr)
					send = (b'.RASname'+data[3:-1]+b'\r')
					conn.sendall(send)
					print("Received: {}".format(data))
					print("Sending: {}".format(send))
				elif str(data[0:2].decode('utf-8')) == ".U":
					send = (b'.UV'+bytes(str(random.randint(1,64)).zfill(3),"utf-8")+b','+bytes(str(random.randint(1,999)).zfill(3),"utf-8")+b'\r')
					conn.sendall(send)
					print("Received: {}".format(data))
					print("Sending: {}".format(send))

				else:
					print("Echoing data...{}".format(data.decode('utf-8')))
					conn.sendall(data)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		main().s.close()