#!/Users/nbd712/.pyenv/versions/3.7.0/bin/python3

import requests, socket, pysnooper, sys, os, time, keyboard

devices = [
			#Enter information as [{Wholer IP},{Wholer Port},{Magnum DST/SRC Size},{Magnum IP},{Magnum Port}]
			['127.0.0.1', 65432, 64, '127.0.0.1',65432,],
			['127.0.0.1', 65431, 64, '127.0.0.1',65431,],
		]

class wholer:
	'''
	The object that represents a 64 channel madi audio device.
	'''

	def __init__(self,hostip,hostport,size,magnum,magport,namelevel="V",):
		self.hostip = hostip
		self.hostport = int(hostport)
		self.magnum = magnum
		self.magport = int(magport)
		self.magSocket = None
		self.namelevel = namelevel						
		self.size = int(size)
		self.routelist = []
		self.names = {
				#destination to name mapping
				#change here to map different names to destinations
				#keep order same from left to right on wholer
				'001':'MADI: 1',
				'002':'MADI: 2',
				'003':'MADI: 3',
				'004':'MADI: 4',
				'005':'MADI: 5',
				'006':'MADI: 6',
				'007':'MADI: 7',
				'008':'MADI: 8',
				'009':'MADI: 9',
				'010':'MADI: 10',
				'011':'MADI: 11',
				'012':'MADI: 12',
				'013':'MADI: 13',
				'014':'MADI: 14',
				'015':'MADI: 15',
				'016':'MADI: 16',
				'017':'MADI: 17',
				'018':'MADI: 18',
				'019':'MADI: 19',
				'020':'MADI: 20',
				'021':'MADI: 21',
				'022':'MADI: 22',
				'023':'MADI: 23',
				'024':'MADI: 24',
				'025':'MADI: 25',
				'026':'MADI: 26',
				'027':'MADI: 27',
				'028':'MADI: 28',
				'029':'MADI: 29',
				'030':'MADI: 30',
				'031':'MADI: 31',
				'032':'MADI: 32',
				'033':'MADI: 33',
				'034':'MADI: 34',
				'035':'MADI: 35',
				'036':'MADI: 35',
				'037':'MADI: 37',
				'038':'MADI: 38',
				'039':'MADI: 39',
				'040':'MADI: 40',
				'041':'MADI: 41',
				'042':'MADI: 42',
				'043':'MADI: 43',
				'044':'MADI: 44',
				'045':'MADI: 45',
				'046':'MADI: 46',
				'047':'MADI: 47',
				'048':'MADI: 48',
				'049':'MADI: 49',
				'050':'MADI: 50',
				'051':'MADI: 51',
				'052':'MADI: 52',
				'053':'MADI: 53',
				'054':'MADI: 54',
				'055':'MADI: 55',
				'056':'MADI: 56',
				'057':'MADI: 57',
				'058':'MADI: 58',
				'059':'MADI: 59',
				'060':'MADI: 60',
				'061':'MADI: 61',
				'062':'MADI: 62',
				'063':'MADI: 63',
				'064':'MADI: 64',
			}

	def magnumConnect(self):
		self.magSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serveraddress = (self.magnum,self.magport)
		try:
			self.magSocket.connect(serveraddress)
			return True
		except Exception as ex:
			print("Device {}: Magnum Server exception raised: {}".format(self.hostip, type(ex).__name__))


	def getAllSRCAlphas(self):
		'''
		Get list of ALL sources
		Interrogate name of source
		update Names dictionary with router names
		'''

		if self.size%8 == 0:
			size = int(self.size/8)
		else:
			size = int((self.size/8)+1)

		#Polls the Magnum server for all of the sources given a destination range.
		#The server responce is parsed into {LEVEL}{DST}{SRC} in the self.routelist variable.
		for i in range(0,size):
			getsrclist = (b'.L'+bytes(self.namelevel,'utf-8')+bytes(str(i+1).zfill(2),'utf-8')+b'\r')
			self.magSocket.sendall(getsrclist)
			#return in .A{level}{dest},{srce}{level}{dest},{srce}
			srclist = str(self.magSocket.recv(83).decode("utf-8"))
			if srclist[0:2] == ".A":
				srclist = [srclist[i:i+8] for i in range(2, len(srclist[1:]), 8)]
				for j in srclist:
					self.routelist += [[j[0],j[1:4],j[5:8]]]
			else:
				print("Server: Incorrect responce received: {}".format(srclist))

		print("Device {}: Received {} destinations from Magnum Server {}".format(self.hostip,len(self.routelist),self.magnum))

		#Takes the routelist variable, and polls the Magnum server for the Mnemonic of the source
		#The output will be added as a fourth cell. The format will be {LEVEL}{DST}{SRC}{SRC_MNEMONIC}
		for i in self.routelist:
			getsrcstr = (b'.RS'+bytes(i[2].zfill(2),'utf-8')+b'\r')
			self.magSocket.sendall(getsrcstr)
			#return in .RA[D/S/L]{mnemonic string}(cr) or .RA[D/S/L]{dest/source/level},{mnemonic string}(cr) depending on version
			srcalpha = str(self.magSocket.recv(16).decode("utf-8"))
			if srcalpha[0:4] == ".RAS":
				i += [srcalpha.partition("\r")[0][4:]]
				#print("Added {} to srcalpha.".format([srcalpha.partition("\r")[0][4:]]))
			else:
				print("Server: Incorrect response received: {}".format(srcalpha))

		#print("Route List: {}".format(self.routelist))

	def assignDST(self):
		'''
		Takes the routelist list and x-ref's the names dictionary with the corresponding sources
		'''
		for i in self.names:
			l = self.names[i]
			for k in self.routelist:
				if int(i) == int(k[1]):
						if self.names[i] != k[3]:
							self.names[i] = k[3]
							print("Device {}: Destination {} name changed from '{}' to '{}'.".format(self.hostip,i,l,self.names[i]))

	def sendHTTP(self):
		print("Server: ***Sample HTTP response***")
		'''
		Will download the current names list from device, alter it, send back changes.
		'''
		#Can't do snything because i dont know the transaction format!
		'''
		try:
			request = requests.get("http://{}:{}/names.xml".format(self.hostip,self.hostport))
		except:
			pass

		headers = {'Content-type': 'text/xml','Connection':'close','Cache-Control':'no-cache'}
		body = {}
		try:
			request = requests.post("http://{}:{}".format(self.hostip,self.hostport),body=body, headers=headers)
		except:
			pass
		'''
		print("Server: Sent new name file to Device: {}.".format(self.hostip))
	
	def getSingleSRCAlpha(self,data):
		#get new source names from Magnum Server
		level, destination, source = data[0], data[1:4], data[5:8]

		#polls server for new name based on source number
		getsrcstr = (b'.RS'+bytes(source,'utf-8')+b'\r')
		self.magSocket.sendall(getsrcstr)
		#return in .RA[D/S/L]{mnemonic string}(cr) or .RA[D/S/L]{dest/source/level},{mnemonic string}(cr) depending on version
		
		#parses response and updates table in routelist source and nmemonic
		srcalpha = str(self.magSocket.recv(16).decode("utf-8"))
		if srcalpha[0:4] == ".RAS":
			output = srcalpha.partition("\r")[0][4:]
			#print("Added {} to srcalpha.".format([srcalpha.partition("\r")[0][4:]]))
		else:
			print("Server: Incorrect response received: {}".format(srcalpha))

		for i in self.routelist:
			if i[1] == destination:
				i[2] = source
				i[3] = output

	def listenUpdate(self,data):
		data = str(data.decode("utf-8"))
		if data[0:2] == ".U" and len(data) > 2:
			#.U{levels}{dest},{srce}(cr)
			print("Device {}: Received new source for destination {}.".format(self.hostip,data.partition('\r')[0][2:]))
			self.getSingleSRCAlpha(data[2:])
			self.assignDST()
			self.sendHTTP()



if __name__ == "__main__":

	os.system("clear")
	start = time.time()
	
	print("Server: Creating devices...")
	for i in devices:
		i += [wholer(i[0],i[1],i[2],i[3],i[4])]
		print("Server: Created device {}...".format(i[5].hostip))

	print("Server: Connecting devices...")
	for i in devices:
		try:
			i[5].magnumConnect()
		except Exception as ex:
			print("Device {}: Excepton raised: {}".format(i[5].hostip,type(ex).__name__))


	print("Server: Getting fresh router names...")
	for i in devices:
		try:
			i[5].getAllSRCAlphas()
		except Exception as ex:
			print("Device {}: Excepton raised: {}".format(i[5].hostip,type(ex).__name__))

	print("Server: Cleaning datasets...")
	for i in devices:
		try:
			i[5].assignDST()
		except Exception as ex:
			print("Excepton raised: {}".format(type(ex).__name__))

	print("Server: Sending changes to Wholers...")
	for i in devices:
		try:
			i[5].sendHTTP()
			pass
		except Exception as ex:
			print("Server: Excepton raised: {}".format(type(ex).__name__))

	
	###Just sending a test command to the server to provoke a response
	time.sleep(1)
	for i in devices:
		try:
			data = (b'.U\r')
			i[5].magSocket.sendall(data)
		except Exception as ex:
			print("Server: Excepton raised: {}".format(type(ex).__name__))

	while True:
		try:
			for i in devices:
				data = i[5].magSocket.recv(1024)
				if data:
					i[5].listenUpdate(data)
		except:
			print("\rServer: Quitting...")
			print("Server: Closing all connections...")
			for i in devices:
				#try:
				i[5].magSocket.shutdown(socket.SHUT_RDWR)
				i[5].magSocket.close()				
				end = time.time()
				print(end-start)
				sys.exit()

#@pysnooper.snoop("/Users/nbd712/output.log")