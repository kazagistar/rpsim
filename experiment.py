#!/usr/bin/python
from math import log
from random import random, sample, randrange
from collections import deque, namedtuple
from os import path
from time import clock

from heapdes import Event, DiscreteEventSimulator

class Experiment:
    """ Represents each experimental run """
    def __init__(self, settings, des, count):
        self.des = des
        self.settings = settings
        self.flux_output = open(path.join(settings['output'], "flux.%i.csv" % count), "w")
        self.positions = [Position(settings, number) for number in xrange(settings["size"])]
        
        self.initial_density(settings)
        # Create the factory for particles

        print("******************************************************")

    def initial_density(self, settings):
        # place particles
        targetDensity = settings["initial_density"]
        width = settings["fatness"]
        length = settings["size"]
        start_time = settings["start_time"]
        
        # place particles randomly into array until density is exceeded (TODO: met not exceeded)
        currentCoverage = 0
        failure_count = 0
        while targetDensity > float(currentCoverage) / length:
            location = randrange(length)
            blocked = False
            lowerBound = max(0, location - width + 1)
            upperBound = min(location + width, length)
            
            for possibleBlocker in self.positions[lowerBound: upperBound]:
                if possibleBlocker.particle != None:
                    blocked = True
                    break
            
            if not blocked:
                self.positions[location].particle = Particle(None, self)
                self.positions[location].particle.index = location
                currentCoverage += width
                failure_count = 0
            else:
                failure_count += 1
            
            assert failure_count < 10000, "Could not fit particle into array"

        # create valid inital next movement times for all particles
        for index, position in reversed(list(enumerate(self.positions))):
            particle = position.particle
            if particle == None:
                continue
            
            # Get new time
            blocker_index = index + width
            if blocker_index < length:
                blocker = self.positions[blocker_index].particle
            else:
                blocker = None
            particle.time = position.nextTime(start_time, blocker)
            if blocker == None:
                self.des.trigger(particle)
    
        # trigger spawns if no blocking particles
        blocked = False
        for possibleBlocker in self.positions[0: width]:
            if possibleBlocker.particle != None:
                blocked = True
                break
        if not blocked:
            self.des.trigger(Spawn(self, start_time))

    def __str__(self):
        return "Experiment["+", ".join(repr(pos.particle) for pos in self.positions)+"]"

class ExperimentSet:
    """ A set of experiments to all be run on the same heap """
    def __init__(self, settings):
        self.des = DiscreteEventSimulator()
        self.experiments = []
        for experiment_number in xrange(settings["runs"]):
            print "Starting experiment " + str(experiment_number)
            self.experiments.append(Experiment(settings, self.des, experiment_number))
        self.ticks = Tick(settings, self)
        self.des.trigger(self.ticks)
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
        self.pauses.append(combined)
        print str(number) + " : " + str(self.pauses)

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
            time = self.pauses[-1].end + nextRandomTime(self.rate)
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

        # If at a flux recording location, store the the time in the record
        if self.experiment.positions[self.index].recorder:
            self.record.append(self.time)

        # Move forward
        self.experiment.positions[self.index].particle = None
        self.index += 1

        # If at the end, store results and remove from list
        if self.index == self.experiment.settings["size"]:
            self.experiment.flux_output.write(",".join(str(time) for time in self.record) + "\n")
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

        # Update density information
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


class Tick(Repeater):
    def __init__(self, settings, experiment_set,):
        Repeater.__init__(self, self.recordDensityPeriod, settings["recording_frequency"])
        self.experiment_set = experiment_set
        self.density_output = open(path.join(settings['output'], "densities.csv"), "w")
        self.start_time = clock()
        self.performance_output = open(path.join(settings['output'], "performance.csv"), "w")

    def recordDensityPeriod(self, time):
        runs = len(self.experiment_set.experiments)
        size  = len(self.experiment_set.experiments[0].positions)
        # Sum the densities at each position over all experiments
        totals = [0.0] * size
        for experiment in self.experiment_set.experiments:
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
        totals = (density / (runs * self.repeat_time) for density in totals)
        # Write to output file as csv (with tab deliminated values)
        self.density_output.write(",".join(str(density) for density in totals) + "\n")

        # Write the events that are currently on the heap at the tick time
        # as well as the time difference since the last tick
        event_count = len(self.experiment_set.des.heap)
        time_spent = clock() - self.start_time
        self.performance_output.write(str(event_count) + "," + str(time_spent) + "\n")

        print str(time) + " (" + str(time_spent) + ")"


class End(Event):
    def __init__(self, time, experiment_set):
        Event.__init__(self, time)
        self.experiment_set = experiment_set

    def run(self, des):
        self.experiment_set.ticks.density_output.close()
        self.experiment_set.ticks.performance_output.close()
        for experiment in self.experiment_set.experiments:
            experiment.flux_output.close()
        self.experiment_set.des.stop()
