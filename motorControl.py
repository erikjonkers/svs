###
 # Author			: E J Jonkers
 # date created		: 14-03-15
 #
###

from time import sleep,time
import Actor
import Queue


class motorControl(Actor.Actor):
	def __init__(self):
		Actor.Actor.__init__(self)
		self.motorUpdateInterval = 0.1 # seconds
		self.acceleration = 0.5 # m/s2
		self.currentSetPoint = (0, 0)  # m/s , timestamp
		self.targetSetPoint = 0
		self.verbose = False
	def recv(self):
		# Receive an incoming message
		try:
			msg = self._msgQueue.get(False)
		except Queue.Empty:
			msg = None
			pass
		if msg is Actor.ActorExit:
			raise Actor.ActorExit()
		return msg
	def setPoint(self, velocity):
		self._msgQueue.put(('setPoint', velocity))
	def setVerbose(self, verbose=False):
		self._msgQueue.put(('verbose', verbose))
	def pvc(self):
		self.printCurrentVelocity()
	def printCurrentVelocity(self):
		print "Vt = %s V = %s" % (round(self.targetSetPoint, 1), round(self.currentSetPoint[0], 1))
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
		if round(v0, 1) == round(vt, 1):
			if self.verbose:
				print "v0 = %s = vt"
			a = 0
		v = v0 + a * dt
		if self.verbose == 2:
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


