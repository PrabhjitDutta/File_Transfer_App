
import os
import socket
from threading import Thread
import time
import sys
import subprocess
import re


class PingThread(Thread):
	def __init__(self, ip):
		Thread.__init__(self)
		self.ip = ip


	def run(self):
		try:
			subprocess.check_output(['ping', self.ip], timeout=9)
		except:
			pass


class Client(Thread):
	def __init__(self, s, addr, buffer):
		Thread.__init__(self)
		self.s = s
		self.addr = addr
		self.buffer = buffer


	def run(self):
		while True:
			size_recv = 0
			time.sleep(0.1)
			size = ((self.s).recv(1024)).decode()
			if not size:
				print("\nPackages Received Sucessfully\n")
				break
			
			size = int(size)

			time.sleep(0.1)
			file_name = ((self.s).recv(1024)).decode()
			file = open(file_name, "wb+")
			file.truncate()

			print("\nReceiving.....")
			while size_recv < size:
				data = ((self.s).recv(self.buffer))
				file.write(data)
				size_recv = (os.stat(file_name)).st_size
				if size_recv == 0:
					break

			print("\nFile Received")
			file.close()


def ipScanner():
	ip_list = socket.gethostbyname_ex(socket.gethostname())[2]

	for ip in ip_list:
		ip = ip.split('.')
		ip = ip[0] + '.' + ip[1] + '.' + ip[2] + '.'

		print("\nScanning for Devices...\n")
		
		for i in range(1, 255):
			ping_ip = ip + str(i)
			newthread = PingThread(ping_ip)
			newthread.start()

	time.sleep(10)
	result = str(subprocess.check_output(['arp', '-a']))
	result = result.split()

	regex = re.compile(r"(19[2-9]\.[\.0-9]+)|(2[0-2][0-3]\.[\.0-9]+)")
	result = list(filter(regex.search, result))
	return result


def receiveMode():
	os.chdir(os.path.expanduser(r'~\Downloads'))

	host = ""
	port = 13000
	buffer = 5120000

	address = (host, port)

	socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socket1.bind(address)
	print("\nWaiting for Sender...")

	try:
		while True:
			socket1.listen(10)
			s, address = socket1.accept()
			
			statement = (s.recv(512)).decode()
			print("\n" + statement)

			while True:
				x = input("Enter y to Receive or n to Reject: ")

				if x == 'y':
					s.send(("accepted").encode())
					new_thread = Client(s, address, buffer)
					new_thread.start()
					break
				elif x == 'n':
					s.send(("rejected").encode())
					break
				else:
					print("Illegal Response Try Again")
					continue


	except KeyboardInterrupt:
		socket1.close()
		sys.exit()


def sendMode():
	ip = "127.0.0.1"

	while True:
		count = 1

		inp = input("Enter ip or scan to Scan for devices: ")
		if inp == 'scan':
			ip_list = ipScanner()
			for i in ip_list:
				print(f"{count}. {i}")
				count+=1

			print(f"{count}. Rescan")
			print(f"{count+1}. Custom IP")
			z = int(input())

			if z != count and z != count+1:
				ip = ip_list[z-1]
				break
			elif z == count:
				continue
			else:
				ip = input("Give IP: ")
				break
		else:
			ip = inp
			break

	host = ip
	port = 13000
	buffer = 5120000

	address = (host, port)

	socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socket2.connect(address)

	file_address = input("\nEnter file Location: ")
	os.chdir(file_address)

	file_names = []

	print("Enter the Name of the File and enter SEND to send them:")
	while True:
		x = input()
		if x == "SEND":
			break
		file_names.append(x)

	print("\nAsking permission from Receiver...")
	socket2.send((ip + " wants to share: " + ' '.join(file_names)).encode())
	response = (socket2.recv(32)).decode()

	if response == 'accepted':
		print("Accepted by Receiver")
		pass
	else:
		print("Rejected by Receiver")
		return -1


	for file_name in file_names:
		try:
			f = open(file_name, "rb+")
		except FileNotFoundError:
			print("No file called {f} present in the Directory".format(f=file_name))
			continue

		time.sleep(1)
		size = str(os.path.getsize(file_name))
		socket2.send(size.encode())

		time.sleep(0.5)
		socket2.send(file_name.encode())
		time.sleep(0.5)

		while True:
			data = f.read(buffer)
			if not data:
				f.close()
				break

			socket2.sendall(data)

		print(f"{file_name} Sent")
		
	socket2.close()


def main():
	print("\n1. Send\n2. Receive")
	choice = int(input())

	if choice == 1:
		sendMode()
	else:
		receiveMode()


if __name__ == '__main__':
	main()	
