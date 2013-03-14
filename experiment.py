#!/usr/bin/python
from math import log
from random import random
from collections import deque

from heapdes import Event, DiscreteEventSimulator

class Experiment(DiscreteEventSimulator):
    """ This class represents each experimental run """
    def __init__(self, settings):
        self.heap = []
        self.positions = [Position(self) for number in xrange(settings.size)]
        self.settings = settings
        self.results = []
        # Create the factory for runners
        self.pushEvent(Factory(settings.count))

def nextRandomTime(rate):
    """ Generates a new time given a rate (which is average delay in ticks)"""
    return (-1.0/rate)*log(random())

class Position:
    """ struct for holding data about positions... determines how next time is generated """
    def __init__(self, number, settings):
        self.runner = None
        self.recorder = number in settings["recorders"]
        self.rate = settings["rate"]

        # read in the pauses {O(n)}
        pauses = []
        for pos, start, end in settings["pauses"]:
            if pos == number:
                pauses.append((start,end))
        # sort the pauses {O(nlogn)}
        pauses.sort()
        # now we need to combine overlapping indexes {O(n)}
        index = 1
        while index < len(self.pauses):
            if pauses[index-1][1] > pauses[index][0]:
                pauses[index-1][1] = pauses[index][1]
                pauses.pop(index)
            else:
                index=index+1
        # at this point, we have in order a list of periods when we will be paused
        # we can access the top of this list in O(1) time and pop it each time
        # this way, the number of pauses do not affect the running time complexity
        # unless
        self.pauses = deque(pauses)

        # strategy pattern: set strategy given in settings file
        if settings["wait_pause"] == 1:
            self.pauseDelay = _waitStrategy()
        else:
            self.pauseDelay = _retryStrategy()
        if settings["wait_block"] == 1:
            self.blockDelay = _waitStrategy()
        else:
            self.blockDelay = _retryStrategy()

    def nextTime(self, time, blocker):
        """ Generate a time to move next, given a current time."""
        time += nextRandomTime(self.rate)
        if (blocker is not None) and (blocker.time >= time): # current time is blocked
            time = blockDelay(time, blocker.time)

        # If the pause has started, go past the pause, remove it, then repeat
        while self.pauses[0][0] < time:
            time = pauseDelay(self.pauses[0][1])
            self.pauses.popleft()

    def _waitStrategy(self, time, end):
        return time + end + nextRandomTime(self.rate)

    def _retryStrategy(self, time, end):
        while time < end:
            time += nextRandomTime(self.rate)
        return time

class Runner(Event):
    """ The runner represents a RNA polymeraze molecule. Each time it moves, it generates a
    "next time" to move."""
    def __init__(self, time, pos):
        Event.__init__(self, time)
        # Start time is stored to measure time spent crossing at the end
        self.record = [time]
        self.pos = pos

    def run(self, experiment):
        # Record the time if we are at a recorder
        if experiment.positions[self.pos].recorder:
            self.record.append(self.time)
        # If at the end, store results and remove from list
        if self.pos >= experiment.settings["size"]:
            experiment.results.append(self.record)
            experiment.positions[self.pos].runner = None
            return
        # Move forward
        experiment.positions[self.pos].runner = None
        self.pos += 1
        experiment.positions[self.pos].runner = self
        # Get new time
        blocker = experiment.positions[self.pos + expertiment.settings["fatness"]]
        self.time = experiment.positions[self.pos].nextTime(self.time, blocker)
        # Requeue
        experiment.pushEvent(self)

    def __str__(self):
        return "Runner(position=" + str(self.pos) + ", time=" + str(self.time) + ")"

class Factory(Event):
    """ Creates Runners at the start of the RNA polymeraze """
    def __init__(self, settings):
        Event.__init__(self, 0)
        self.maxcount = settings["count"]
        self.rate = settings["rate"] * settings["density"]


    def run(self, experiment):
        # If there not room, wait to try again. Otherwise, make a new runner
        for position in experiment.positions[0:experiment.settings["fatness"]]:
            if position.runner is not None:
                if experiment.settings["wait_block"] == 1:
                    self.time = position.runner.time
                    self.time += nextRandomTime(self.rate)
                else:
                    while self.time < position.runner.time:
                        self.time += nextRandomTime(self.rate)

                experiment.pushEvent(self)
                return

        # Generate a new runner, and give it a proper time to move
        new = Runner(self.time, 0)
        blocker = experiment.positions[self.pos + expertiment.settings["fatness"]]
        new.time = experiment.positions[0].nextTime(new.time, blocker)
        experiment.positions[0].runner = new
        experiment.pushEvent(new)
        self.maxcount -= 1
        if self.maxcount > 0:
            experiment.pushEvent(self)

    def __str__(self):
        return "Factory(maxcount=" + str(self.maxcount) + ", time=" + str(self.time) + ")"


class Repeater(Event):
    """ A utility event for adding in extra functionality. It runs a given function on a set frequency """
    def __init__(self, function, repeat_time):
        Event.__init__(self, 0)
        self.function = function
        self.repeat_time = repeat_time

    def run(self, experiment):
        self.function(experiment, self.time)
        self.time += self.repeat_time
        experiment.pushEvent(self)
