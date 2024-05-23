from pynput.keyboard import Key, Controller
import threading as th
import socket

class remotePlayers(object):
	def __init__(self):
		self.players = {
			# "1": {
			# 	"ip": None,
			# 	"keys": {
			# 		"w": "w",
			# 		"a": "a",
			# 		"d": "d",
			# 		"s": "s",
			# 		"j": "j",
			# 		"k": "k",
			# 		"l": "l",
			# 		";": ";"
			# 	}
			# },
			"2": {
				"ip": None,
				"keys": {
					ord("w"): ord("t"),
					ord("a"): ord("f"),
					ord("d"): ord("h"),
					ord("s"): ord("g"),
					ord("j"): ord("1"),
					ord("k"): ord("2"),
					ord("l"): ord("3"),
					ord(";"): ord("4")
				}
			},
			"3": {
				"ip": None,
				"keys": {
					ord("w"): ord("z"),
					ord("a"): ord("c"),
					ord("d"): ord("v"),
					ord("s"): ord("x"),
					ord("j"): ord("b"),
					ord("k"): ord("n"),
					ord("l"): ord("m")
				}
			},
			"4": {
				"ip": None,
				"keys": {
					ord("w"): 38,
					ord("a"): 40,
					ord("d"): 37,
					ord("s"): 39,
					ord("j"): ord("7"),
					ord("k"): ord("8"),
					ord("l"): ord("9"),
					ord(";"): ord("0")
				}
			}
		}
		# label the players
		# set controls for each play
		# let player know what player they are

		'''
			player 1:
				w -> up
				a -> left
				d -> right
				s -> down
				j -> shoot
				k -> special
				l -> meele
				; -> flex
			player 2:
				t -> up
				f -> left
				h -> right
				g -> down
				/ -> shoot
				* -> special
				- -> meele
				+ -> flex
			player 3:
				i -> up
				k -> down
				j -> left
				l -> right
				4 -> shoot
				5 -> special
				6 -> meele
			player 4:
				up arr -> up
				down arr -> down
				left arr -> left
				right arr -> right
				7 -> shoot
				8 -> special
				9 -> meele
		'''
	
	def addPlayer(self, ip):
		available_players = self.getAvailablePlayers()

		if len(available_players) < 4:
			player = self.alreadyAPlayer(ip)
			if player:
				return player

		if len(available_players) > 0:
			player = available_players[0]
			self.players[player]['ip'] = ip
			return self.players[player]
		return None

	def alreadyAPlayer(self, ip):
		for player in self.players:
			if self.players[player]['ip'] == ip:
				return self.players[player]
		return None

	def getAvailablePlayers(self):
		avail = {}
		for player in self.players:
			if not self.players.get(player).get('ip'):
				avail.update({player: self.players[player]})

		return [key for key in list(avail.keys())]

class remoteKeyboardHost(object):
	def __init__(self, remotePlayers, conn):
		self.conn = conn
		self.GOOD = b'1'
		self.BAD = b'0'
		self.keyboard = Controller()
		player_ip, port = conn.getsockname()
		self.player = remotePlayers.addPlayer(player_ip)

	def press_key(self, key):
		playerKeys = self.player['keys']
		if ord(key) in list(playerKeys.keys()):
			print(key, 'pressed and translated to:', key.translate(playerKeys) )
			# self.keyboard.press(key)
		self.conn.send(self.GOOD)

	def release_key(self, key):
		playerKeys = self.player['keys']
		if ord(key) in list(playerKeys.keys()):
			print(key, 'released and translated to:', key.translate(playerKeys) )
			# self.keyboard.release(key)
		self.conn.send(self.GOOD)

	def handle_key(self, key_info):
		key, state = tuple( key_info.decode().split('-') )
		action = {
			'p': self.press_key,
			'r': self.release_key
		}
		action[state](key)

	def handle(self):
		key_info = self.conn.recv(3)
		self.handle_key(key_info)

class server(object):
	def __init__(self, serverModule=None, host='0.0.0.0', port=5600):
		self.module = serverModule
		self.threads = 4
		self.players = remotePlayers()
		self.host = host
		self.port = port
		self.pendingConnections = 1

		# AF_INET -> is ipv4
		# SOCK_STREAM -> TCP
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind( (self.host, self.port) )
		self.socket.listen(self.pendingConnections)

	def test_server(self, conn):
		data = conn.recv(1)
		print(data)
		conn.send(b'ok 1')
		data = conn.recv(1)
		print(data)
		conn.send(b'ok 2')
		data = conn.recv(1)
		print(data)
		conn.send(b'ok 3')

	def handle_connection(self, conn):
		if self.module:
			while True:
				self.module(self.players, conn).handle()
		else:
			self.test_server(conn)

	def get_connections(self):
		while True:
			conn, addr = self.socket.accept()
			ip, port = addr
			if self.threads >= th.active_count():
				thread = th.Thread( target=self.handle_connection, args=[conn] )
				thread.start()

	def listen(self):
		print(f'Server running on -> {self.host}:{self.port}')
		self.get_connections()

	def run(self):
		self.listen()

server( remoteKeyboardHost ).run()