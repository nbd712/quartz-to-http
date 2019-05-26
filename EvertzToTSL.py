#!/Users/nbd712/.pyenv/versions/3.7.0/bin/python3

import requests, socket, sys, os, time, re
from urllib.parse import quote

devices = [
			#Enter information as [{Wholer IP},{Wholer Port},{Magnum DST/SRC Size},{Magnum IP},{Magnum Port}]
			['10.77.60.217', 80, 64, '10.10.200.91',65432,],
			#['127.0.0.1', 80, 64, '10.10.200.91',65431,],
			#['127.0.0.1', 80, 64, '127.0.0.1',65400,],
			#['127.0.0.1', 80, 64, '127.0.0.1',65403,],
			#['127.0.0.1', 80, 64, '127.0.0.1',65404,],
			#['127.0.0.1', 80, 64, '127.0.0.1',65405,],
			#['127.0.0.1', 80, 64, '127.0.0.1',65406,],
			#['127.0.0.1', 80, 64, '127.0.0.1',65407,],
			#['127.0.0.1', 80, 64, '127.0.0.1',65408,],
			#['127.0.0.1', 80, 64, '127.0.0.1',65409,],
		]

class wholer:
	'''
	The object that represents a 64 channel madi audio device.
	'''

	def __init__(self,hostip,hostport,size,magnum,magport,namelevel="V",):
		self.hostip = hostip
		self.hostport = int(hostport)
		self.devname = self.hostip
		self.magnum = str(magnum)
		self.magport = int(magport)
		self.magSocket = None
		self.namelevel = namelevel
		self.size = int(size)
		self.success = False
		self.routelist = []
		self.names = {
				#destination to name mapping
				#change here to map different names to destinations
				#keep order same from left to right on wholer
				'1':'MADI : 1',
				'2':'MADI : 2',
				'3':'MADI : 3',
				'4':'MADI : 4',
				'5':'MADI : 5',
				'6':'MADI : 6',
				'7':'MADI : 7',
				'8':'MADI : 8',
				'9':'MADI : 9',
				'10':'MADI : 10',
				'11':'MADI : 11',
				'12':'MADI : 12',
				'13':'MADI : 13',
				'14':'MADI : 14',
				'15':'MADI : 15',
				'16':'MADI : 16',
				'17':'MADI : 17',
				'18':'MADI : 18',
				'19':'MADI : 19',
				'20':'MADI : 20',
				'21':'MADI : 21',
				'22':'MADI : 22',
				'23':'MADI : 23',
				'24':'MADI : 24',
				'25':'MADI : 25',
				'26':'MADI : 26',
				'27':'MADI : 27',
				'28':'MADI : 28',
				'29':'MADI : 29',
				'30':'MADI : 30',
				'31':'MADI : 31',
				'32':'MADI : 32',
				'33':'MADI : 33',
				'34':'MADI : 34',
				'35':'MADI : 35',
				'36':'MADI : 35',
				'37':'MADI : 37',
				'38':'MADI : 38',
				'39':'MADI : 39',
				'40':'MADI : 40',
				'41':'MADI : 41',
				'42':'MADI : 42',
				'43':'MADI : 43',
				'44':'MADI : 44',
				'45':'MADI : 45',
				'46':'MADI : 46',
				'47':'MADI : 47',
				'48':'MADI : 48',
				'49':'MADI : 49',
				'50':'MADI : 50',
				'51':'MADI : 51',
				'52':'MADI : 52',
				'53':'MADI : 53',
				'54':'MADI : 54',
				'55':'MADI : 55',
				'56':'MADI : 56',
				'57':'MADI : 57',
				'58':'MADI : 58',
				'59':'MADI : 59',
				'60':'MADI : 60',
				'61':'MADI : 61',
				'62':'MADI : 62',
				'63':'MADI : 63',
				'64':'MADI : 64',
			}

		'''
		#easy way to put them back
		self.sendHTTP()
		sys.exit()
		'''

		self.getName()

		#Connect to magnum server
		if not self.magnumConnect():
			return

		#Get list of sources / get names of sources / update var names
		try:
			self.getAllSRCAlphas()
		except Exception as ex:
			print("Device {}: Excepton raised: {}".format(self.devname,type(ex).__name__))

		#Assigning names to appropriate destination
		print("Server: Cleaning up datasets for {}.".format(self.devname))
		try:
			self.assignDST()
		except Exception as ex:
			print("Excepton raised: {}".format(type(ex).__name__))

		#Initial HTTP Interaction with wholer device
		print("Server: Compiling HTTP response.")
		try:
			self.sendHTTP()
		except Exception as ex:
			print("Server: Excepton raised: {}".format(type(ex).__name__))

		self.success = True


	def getName(self):
		#Will poll the Wholer/Device for it's name and set it as self.devname variable
		#if name is not found, set IP as device name
		#below is temporary
		self.devname = "Wholer #{}".format(str(self.hostport)[-2:])

	def magnumConnect(self):
		print("Device {}: Connecting to Magnum Server...".format(self.devname))
		self.magSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#serveraddress = (self.magnum,self.magport)
		serveraddress = (self.magnum, self.magport)
		try:
			self.magSocket.connect(serveraddress)
			print("Device {}: Established conection to Magnum Server.".format(self.devname))
			return True
		except Exception as ex:
			print("Device {}: Magnum Server exception raised: {}".format(self.devname, type(ex).__name__))
			print("Device {}: Unable to connect to Magnum Server.".format(self.devname))

	def getAllSRCAlphas(self):
		'''
		Get list of ALL sources
		Interrogate name of source
		update Names dictionary with router names
		'''
		print("Device {}: Polling Magnum server for names...".format(self.devname))

		if self.size%8 == 0:
			size = int(self.size/8)
		else:
			size = int((self.size/8)+1)

		#Polls the Magnum server for all of the sources given a destination range.
		#The server response is parsed into {LEVEL}{DST}{SRC} in the self.routelist variable.
		for i in range(1,size):
			getsrclist = (b'.L'+bytes(self.namelevel,'utf-8')+bytes(str(int(i*9)-9),'utf-8')+b',-\r')
			self.magSocket.sendall(getsrclist)
			#return in .A{level}{dest},{srce}{level}{dest},{srce}
			srclist = str(self.magSocket.recv(1024).decode("utf-8"))
			if srclist[0:2] == ".A":
				srclist = re.findall(r'[A-Z][\d]+[\D]+[\d]+',srclist[2:])
				for j in srclist:
					self.routelist += [list(re.findall(r'(\w)(\d+)(?:,)(\d+)',j)[0])]
			elif srclist[0:2] == ".E":
				print("Server: Unexpected end of Magnum response...")
				break
			else:
				print("Server: Incorrect response received: {}".format(srclist))

		print("Device {}: Received {} destinations from Magnum Server: {}".format(self.devname,len(self.routelist),self.magnum))

		#Takes the routelist variable, and polls the Magnum server for the Mnemonic of the source
		#The output will be added as a fourth cell. The format will be {LEVEL}{DST}{SRC}{SRC_MNEMONIC}
		for i in self.routelist:
			#remove "+int(i[1])" when not testing
			getsrcstr = (b'.RS'+bytes(str(int(i[2])),'utf-8')+b'\r')
			self.magSocket.sendall(getsrcstr)
			#return in .RA[D/S/L]{mnemonic string}(cr) or .RA[D/S/L]{dest/source/level},{mnemonic string}(cr) depending on version
			srcalpha = str(self.magSocket.recv(1024).decode("utf-8"))
			if srcalpha[0:4] == ".RAS":
				i += re.findall(r'.RAS\d+,(.+)(?=[\W])',srcalpha)
				#print("Added {} to srcalpha.".format([srcalpha.partition("\r")[0][4:]]))
			elif re.findall(r'^[\D][\D]',srcalpha)[0] == ".E": #tried to be cute with regex <3
				print("Server: Magnum server {} returned error: {}".format(self.magnum, srcalpha))
			else:
				print("Server: Incorrect response received: {}".format(srcalpha))


	def assignDST(self):
		'''
		Takes the routelist list and x-ref's the names dictionary with the corresponding sources
		'''
		for i in self.names:
			l = self.names[i]
			for k in self.routelist:
				if int(i) == int(k[1]):
						try:
							if self.names[i] != k[3]:
								self.names[i] = k[3]
								print("Device {}: Destination {} name changed from '{}' to '{}'.".format(self.devname,i,l,self.names[i]))
						except:
							k += [self.names[i]]


	def sendHTTP(self):
		'''
		Will download the the current names, compare to dictionary, make changes, send it back.
		'''
		#Can't do anything because i dont know the transaction format!
		#http://10.77.60.217/names.cgi?name0:Madi%20:%201
		counter = 0
		for i in self.names:
			sendstr = "http://{}:{}/names.cgi?name{}:{}".format(self.hostip,self.hostport,counter,quote(self.names[i]))
			request = requests.get(url = sendstr)
			counter += 1
			#print(sendstr)

			#print(request)

		print("Server: Sent new name file to Device: {}.".format(self.devname))

	def getSingleSRCAlpha(self,data):
		#get new source names from Magnum Server
		_, level, destination, source = re.findall(r'(.\D)(\D)(\d+),(\d+)',data)[0]

		#polls server for new name based on source number
		getsrcstr = (b'.RS'+bytes(source,'utf-8')+b'\r')
		self.magSocket.sendall(getsrcstr)
		#return in .RA[D/S/L]{mnemonic string}(cr) or .RA[D/S/L]{dest/source/level},{mnemonic string}(cr) depending on version

		#parses response and updates table in routelist source and nmemonic
		srcalpha = str(self.magSocket.recv(1024).decode("utf-8"))
		if re.findall(r'^(\D+)',srcalpha)[0] == ".RAS":
			output = re.findall(r'^(\D+)(\d+),(.+)(?=[\W])',srcalpha)[0]
			#print("Added {} to srcalpha.".format([srcalpha.partition("\r")[0][4:]]))

			for i in self.routelist:
				if i[1] == destination:
					i[2] = output[1]
					i[3] = output[2]
		elif re.findall(r'^(\D{2})',srcalpha)[0] == ".E":
			print("Server: Magnum server unable to find source number.")
		else:
			print("Server: Incorrect response received: {}".format(srcalpha))



	def listenUpdate(self,data):
		#data = data.decode('utf-8')
		data = re.findall(r'(?!\r)\D+\d+,\d+',data.decode('utf-8'))
		for i in data:
			if re.findall(r'^[\D][\D]',i)[0] == ".U":
				#.U{levels}{dest},{srce}(cr)
				print("Device {}: Received new source for destination {}.".format(self.devname, re.findall(r'(\D+)(\d+)(,\d+)',i)[0][1]))
				self.getSingleSRCAlpha(i)
			#Add in if statement for .P command and .A command
			else:
				print("Server: Unexpected message from Magnum: {}".format(i))

		self.assignDST()
		self.sendHTTP()

if __name__ == "__main__":

	os.system("clear")
	start = time.time()

	print("Server: Creating devices...")
	for i in devices:
		i += [wholer(i[0],i[1],i[2],i[3],i[4])]
		if i[5].success:
			print("Server: Done creating device {}...".format(i[5].devname))
		else:
			print("Server: Was not able to create the device {}.".format(i[5].hostip))

	print("Server: Listening for updates...")
	while True:
		try:
			for i in devices:
				if i[5].success:
					data = i[5].magSocket.recv(1024)
					if data:
						i[5].listenUpdate(data)
				else:
					pass
			#raise Exception("Asserted exception.")
		except:
			print("\rServer: Quitting...")
			print("Server: Closing all connections...")
			for i in devices:
				try:
					i[5].magSocket.shutdown(socket.SHUT_RDWR)
					i[5].magSocket.close()
				except:
					print("Server: Unable to close connection for {}. Guess it wasn't open.".format(i[5].devname))
			sys.exit()
