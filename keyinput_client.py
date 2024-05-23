from pynput.keyboard import Key, Listener
import threading as th
import socket

class remoteKeyboardClient(object):
	def __init__(self, conn):
		self.conn = conn

	def on_press(self, key):
		try:
			_key = key.char
		except AttributeError:
			return None

		if key.char not in list('wasdjkl;'):
			return None

		self.conn.send(f'{key.char}-p'.encode())
		status = self.conn.recv(1)
		if int( status.decode() ) != 1:
			self.on_press(key)
		print(f'{key} press signal sent')
		print(f'server status on {key}: {int(status.decode())}')

	def on_release(self, key):
		try:
			_key = key.char
		except AttributeError:
			return None

		if key.char not in list('wasdjkl;'):
			return None

		self.conn.send(f'{key.char}-r'.encode())
		status = self.conn.recv(1)
		if int( status.decode() ) != 1:
			self.on_release(key)
		print(f'{key} release signal sent')

	def startKeyListener(self):
		listener = Listener( 
			on_press=self.on_press, 
			on_release=self.on_release
		)
		listener.start()
		listener.join()

	def handle(self):
		# get key inputs
		self.startKeyListener()

class client(object):
	def __init__(self, clientModule=None, host='localhost', port=5600):
		self.module = clientModule
		self.host = host
		self.port = port

		# AF_INET -> ipv4
		# SOCK_STREAM -> TCP
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	def test_client(self):
		self.socket.send(b'1')
		data = self.socket.recv(4)
		print(data)
		self.socket.send(b'2')
		data = self.socket.recv(4)
		print(data)
		self.socket.send(b'3')
		data = self.socket.recv(4)
		print(data)

	def handle_connection(self):
		if self.module:
			self.module(self.socket).handle()
		else:
			self.test_client()

	def connect(self):
		print(f'Connected to: {self.host}:{self.port}')
		try:
			self.socket.connect( (self.host, self.port) )
		except ConnectionRefusedError:
			print('No connection could be made because the target machine actively refused it')
		self.handle_connection()

	def run(self):
		self.connect()

HOST = "192.168.8.169"

client( remoteKeyboardClient, host=HOST ).run()