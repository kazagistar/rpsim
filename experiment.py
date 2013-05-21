#!/usr/bin/python
from math import log
from random import random, sample
from collections import deque, namedtuple
from os import path

from heapdes import Event, DiscreteEventSimulator

class Experiment:
	""" Represents each experimental run """
	def __init__(self, settings, des, count, output_folder):
		self.des = des
		self.settings = settings
		self.flux_output = open(path.join(output_folder, "flux.%i.csv" % count), "w")
		self.positions = [Position(settings, number) for number in xrange(settings["size"])]
		# Create the factory for particles
		self.des.trigger(Spawn(self, 0))

	def __str__(self):
		return "Experiment["+", ".join(repr(pos.particle) for pos in self.positions)+"]"

class ExperimentSet:
	""" A set of experiments to all be run on the same heap """
	def __init__(self, settings, output_folder):
		self.des = DiscreteEventSimulator()
		self.experiments = []
		for experiment_count in xrange(settings["runs"]):
			print "Starting experiment " + str(experiment_count)
			self.experiments.append(Experiment(settings, self.des, experiment_count, output_folder))
		self.density_recorder = DensityRecorder(settings, self.experiments, output_folder)
		self.des.trigger(self.density_recorder)
		self.des.trigger(End(settings["time"], self))

	def run(self):
		self.des.run()

def nextRandomTime(rate):
	""" Generates a new time given a rate (which is average delay in ticks)"""
	return (-1.0/rate)*log(random())

Pause = namedtuple("Pause", ["start", "end"])

class Position:
	""" struct for holding data about positions... determines how next time is generated """
	def __init__(self, settings, number):
		self.particle = None
		self.recorder = number in settings["recorders"]
		self.rate = settings["beta"]
		self.density = 0.0

		# filter in the pauses for this location {O(n)}
		pauses = [Pause(start, end) for pos, start, end in settings["pauses"] if pos == number]

		# sort the pauses {O(nlogn)}
		pauses.sort()
		# combine overlapping pauses, and build a new list in reverse {O(n)}
		# uses an accumulator "combined" to combine overlapping pauses, and
		# then once all overlapping pauses are combined, adds it to the final
		# pause list. It is last to first, so the resulting list is last to
		# first and can be treated like a stack.
		self.pauses = []
		# early exit if we don't have to deal with pauses
		if not pauses:
			return
		combined = pauses.pop()
		for previous in reversed(pauses):
			if previous.end >= combined.start:
				combined = Pause(previous.start, combined.end)
			else:
				self.pauses.append(combined)
				combined = previous

	def nextTime(self, time, blocker):
		""" Generate a time to move next, given a current time. """
		# If we are blocked, don't start calculating time til after the block
		if (blocker is not None) and (blocker.time >= time):
			time = blocker.time

		# Generate a next time to move
		time += nextRandomTime(self.rate)
		# Skip
		while self.pauses and time > self.pauses[-1].end:
			self.pauses.pop()
		# If the pause has started, go past the pause, remove it, then repeat
		while self.pauses and self.pauses[-1].start < time:
			time = pauses[-1].end + nextRandomTime(self.rate)
			while self.pauses and time > self.pauses[-1].end:
				self.pauses.pop()
		return time


class Particle(Event):
	""" The particle represents a RNA polymeraze molecule. Each time it moves, it generates a
	"next time" to move."""
	def __init__(self, time, experiment):
		Event.__init__(self, time)
		self.experiment = experiment
		self.index = 0
		self.record = [time]

	def run(self, des):
		# If we are unblocking a runner, queue it up
		if self.index >= self.experiment.settings["fatness"]:
			unblocked = self.experiment.positions[self.index - self.experiment.settings["fatness"]].particle
			if unblocked:
				des.trigger(unblocked)

		# Move forward
		self.experiment.positions[self.index].particle = None
		self.index += 1

		# If at the end, store results and remove from list
		if self.index == self.experiment.settings["size"]:
			self.experiment.flux_output.write("\t".join(str(time) for time in self.record) + "\n")
			return
		self.experiment.positions[self.index].particle = self

		# If moved past the "fatness" index, trigger a spawn
		if self.index == self.experiment.settings["fatness"]:
			des.trigger(Spawn(self.experiment, self.time))

		# Get new time
		blocker_index = self.index + self.experiment.settings["fatness"]
		if blocker_index < self.experiment.settings["size"]:
			blocker = self.experiment.positions[blocker_index].particle
		else:
			blocker = None
		new_time = self.experiment.positions[self.index].nextTime(self.time, blocker)
		# Update density information
		self.experiment.positions[self.index].density += new_time - self.time
		self.time = new_time

		# Requeue if not blocked
		if not blocker:
			des.trigger(self)

	def __str__(self):
		return "Particle(position=" + str(self.index) + ", time=" + str(self.time) + ")"

class Spawn(Event):
	""" Creates particles at the start of the RNA polymeraze """
	def __init__(self, experiment, time):
		time += nextRandomTime(experiment.settings["alpha"])
		Event.__init__(self, time)
		self.experiment = experiment

	def run(self, des):
		# Generate a new particle, and give it a proper time to move
		blocker = self.experiment.positions[self.experiment.settings["fatness"]].particle
		new = Particle(self.experiment.positions[0].nextTime(self.time, blocker), self.experiment)
		self.experiment.positions[0].particle = new
		# Record density
		self.experiment.positions[0].density += new.time - self.time
		# Queue if not blocked
		if not blocker:
			des.trigger(new)

	def __str__(self):
		return "Spawn(time=" + str(self.time) + ")"


class Repeater(Event):
	""" A utility event for adding in extra functionality. It runs a given function on a set frequency """
	def __init__(self, function, repeat_time):
		Event.__init__(self, 0)
		self.function = function
		self.repeat_time = repeat_time

	def run(self, des):
		self.function(self.time)
		self.time += self.repeat_time
		des.trigger(self)


class DensityRecorder(Repeater):
	def __init__(self, settings, experiments, output_folder):
		Repeater.__init__(self, self.recordDensityPeriod, settings["recording_frequency"])
		self.experiments = experiments
		self.output = open(path.join(output_folder, "densities.csv"), "w")

	def recordDensityPeriod(self, time):
		print time
		size = len(self.experiments[0].positions)
		runs = len(self.experiments)
		# Sum the densities at each position over all experiments
		totals = [0.0] * size
		for experiment in self.experiments:
			for index, position in enumerate(experiment.positions):
				# Roll over any time on the particle to the next recording
				if position.particle:
					leftover = (position.particle.time - time)
					totals[index] += position.density - leftover
					position.density = leftover
				else:
					totals[index] += position.density
					position.density = 0
		# Divide by number of positions to get average
		totals = (density / runs for density in totals)
		# Write to output file as csv (with tab deliminated values)
		self.output.write("\t".join(str(density) for density in totals) + "\n")


class End(Event):
	def __init__(self, time, experiment_set):
		Event.__init__(self, time)
		self.experiment_set = experiment_set

	def run(self, des):
		self.experiment_set.density_recorder.recordDensityPeriod(time)
		self.experiment_set.density_recorder.output.close()
		self.experiment_set.des.stop()
