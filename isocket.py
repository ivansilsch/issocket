
import os
import pyinotify
import sys

class Socket(pyinotify.ProcessEvent):

	""" Socket simulation uses a directory scanner for new incoming data simulation on files """

	def __init__(self):

		# The file used to scan and get new data
		self.file = None

		# A queue for new incoming data
		self.msg_queue = []

		# The socket begins the scanning for its file for new incoming data.
		self.listening = False

		# Used when text written into the file its new.
		# Allows the data flow blocking if not changed.
		self.is_ignored = True

		# watch_manager : It is the file changes scanner.
		# Used when a new changed is detected, if it happen,
		# watch_manager along self.notifier detect changes,
		# update the queue, and set the new state.
		watch_manager = pyinotify.WatchManager()
		watch_manager.add_watch('%s/active' % sys.path[0], pyinotify.IN_MODIFY)
		self.notifier = pyinotify.ThreadedNotifier(watch_manager, self)

	def bind(self, address, port):
		""" Asociate the addres and port with the socket. """

		self.address = '%s:%s' % (address, port)
		try:
			self.file = open('./active/%s' % self.address, 'x')
		except Exception as e:
			print('[Error] Socket in use %s' % self.address)

	def listen(self):
		""" The socket is now capable of detect changes of its respective file."""
		self.listening = True
		self.notifier.start()

	def accept(self):
		pass

	def close(self):
		""" Close the connection and removes the socket file. """
		if self.file:
			self.file.close()
		os.system('rm ./active/%s' % self.address)

	def send(self, data):
		with open('./active/%s' % self.address, 'w') as file:
			file.write(data)

	def recv(self):

		# Guarrantee the queue has new data,
		# if it is not the case it will be blocked until new data is detected
		if self.listening:

			while self.is_ignored:
				# Blocking loop
				pass

			data = self.msg_queue[0]
			self.msg_queue = self.msg_queue[1:]

			self.is_ignored = True
			return data

		else:
			raise Exception('[Err] The socket is not listening')
			exit()

	def connect(self, address, port):
		""" Asociate the addres for use in remote mode. (read only) """
		address = '%s:%s' % (address, port)
		try:
			self.file = open('./active/%s' % address, 'r')
			self.address = address
		except Exception as e:
			print('[Error] Could not connect to %s' % address)

	def process_IN_MODIFY(self, event):
		if self.address == event.pathname.split('/')[-1]:

			with open('./active/%s' % self.address, 'r') as file:
				data = file.read()
				self.msg_queue.append(data)

			# Unlock the receiver socket method
			self.is_ignored = False
