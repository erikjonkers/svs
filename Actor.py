###
 # Author			: E J Jonkers
 # date created		: 14-03-15
 #
###

from threading import Thread, Event
import Queue

# Sentinel used for shutdown
class ActorExit(Exception):
	pass

class Actor:
	def __init__(self):
		self._msgQueue = Queue.Queue()

	def send(self, msg):
		'''
		Send a message to the actor
		'''
		self._msgQueue.put(msg)

	def recv(self):
		'''
		Receive an incoming message
		'''
		msg = self._msgQueue.get()
		if msg is ActorExit:
			raise ActorExit()
		return msg

	def close(self):
		'''
		Close the actor, thus shutting it down
		'''
		self.send(ActorExit)

	def start(self):
		'''
		Start concurrent execution
		'''
		self._terminated = Event()
		t = Thread(target=self._bootstrap)
		t.daemon = True
		t.start()

	def _bootstrap(self):
		try:
			self.run()
		except ActorExit:
			pass
		finally:
			self._terminated.set()

	def join(self):
		self._terminated.wait()

	def run(self):
		'''
		Run method to be implemented by the user
		'''
		while True:
			msg = self.recv()

# Sample ActorTask
class PrintActor(Actor):
	def run(self):
		while True:
			msg = self.recv()
			print('Got:', msg)


