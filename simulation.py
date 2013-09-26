#!/usr/bin/python
from heapq import heappush, heappop

class Simulation:
	def __init__(self, settings):
        self.settings = settings
        *settings["plugins"]
		self.heap = []
		self.running = True
	
	def trigger(self, event):
		""" pushes a event to be resolved """
		heappush(self.heap, (event.time, event))
	
	def run(self):
		self.running = True
		while self.running:
			time, event = heappop(self.heap)
			event.run(self)
		
	def stop(self):
		self.running = False


class Event:
	""" Events are placed in a heap, sorted in decreasing order according to 
	what time they fire. They must all implement a run function, which is reponsible 
	for processing them and placing them back in the queue with a new, higher time. """
	def __init__(self, time):
		self.time = time
	
	def run(self, des):
		raise NotImplementedError("Must extend event class to use")
	
	# Implementing a __str__ is recommended for debugging
