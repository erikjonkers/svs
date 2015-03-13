###
 # Author			: E J Jonkers
 # date created		: 27-02-15
 #
###

import Queue
from threading import Thread, Event
from time import sleep,time

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

class motorControl(Actor):
	def __init__(self):
		Actor.__init__(self)
		self.motorUpdateInterval = 0.1 # seconds
		self.acceleration = 0.5 # m/s2
		self.currentSetPoint = (0, 0)  # m/s , timestamp
		self.targetSetPoint = 0
		self.verbose = False
	def recv(self):
		'''
		Receive an incoming message
		'''
		try:
			msg = self._msgQueue.get(False)
		except Queue.Empty:
			msg = None
			pass
		if msg is ActorExit:
			raise ActorExit()
		return msg

	def setPoint(self, velocity):
		self._msgQueue.put(velocity)
	def calculateSetPoint(self):
		t = time()
		v0 = self.currentSetPoint[0]
		vt = self.targetSetPoint
		t0 = self.currentSetPoint[1]
		if t0 == 0:
			t0 = t
		dt = t - t0
		a = self.acceleration
		if v0 > vt:
			# slow down
			a = self.acceleration * -1
		if round(v0, 2) == round(vt, 2):
			a = 0
		v = v0 + a * dt
		if self.verbose:
			print "v0=%s vt=%s a=%s " % (v0,vt,a)
		self.currentSetPoint = (v, t)
		return v
	def checkMessage(self):
		msg = self.recv()
		if msg is not None:
			# msg should be a typle ( cmd, value )
			if msg[0] == 'verbose':
				self.verbose = msg[1]
			if msg[0] == 'setPoint':
				self.targetSetPoint = msg[1]

	def run(self):
		while True:
			setPoint = self.calculateSetPoint()
#			print 'new setPoint:', setPoint
			sleep(self.motorUpdateInterval)
			self.checkMessage()

# Sample use
#p = PrintActor()
#p.start()
#p.send(('type','Hello'))
#p.send('World')
#p.close()
#p.join()

#pp = motorControl()
#pp.start()
#sleep(2)
#pp.setPoint(1) # 1 m/s
#sleep(5)
#pp.close()
#pp.join()
