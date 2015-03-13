###
 # Author			: E J Jonkers
 # company			: DataCT	
 # date created		: 27-02-15
 # date modified	: $Id$
 #
###

from Queue import Queue
from threading import Thread, Event
from time import sleep

# Sentinel used for shutdown
class ActorExit(Exception):
	pass

class Actor:
	def __init__(self):
		self._msgQueue = Queue()

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

class motorControl(Actor):
	def __init__(self):
		Actor.__init__(self)
		self.motorUpdateInterval = 1.0 # seconds
		self.acceleration = 1 # m/s2
		self.currentSetPoint = (0, 0)  # m/s , timestamp
		self.targetSetPoint = 0
	def setPoint(self, velocity):
		self._msgQueue.put(velocity)
	def calculateSetPoint(self):
		t = time()
		v0 = self.currentSetPoint[0]
		dt = t - self.currentSetPoint[1]
		v = v0 + self.acceleration * dt
		self.currentSetPoint = (v, t)
		return v
	def run(self):
		while True:
			setPoint = self.calculateSetPoint()
			print 'new setPoint:', self.targetSetPoint
			sleep(self.motorUpdateInterval)
			self.targetSetPoint = self.recv()

# Sample use
#p = PrintActor()
#p.start()
#p.send(('type','Hello'))
#p.send('World')
#p.close()
#p.join()

pp = motorControl()
pp.start()
pp.setPoint(1) # 1 m/s
#sleep(1.2)
#pp.setPoint('fast')
#pp.setPoint('medium')
sleep(5)
pp.close()
pp.join()
