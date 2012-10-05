#!/usr/bin/python
from heapq import heappush
import sys
from math import log
from random import random


def nextRandomTime(rate):
    """ Generates a new time given a rate (which is average delay in ticks)"""
    return (-1.0/rate)*log(random())




    

class Runner(Event):
    """ The runner represents a RNA polymeraze molecule. Each time it moves, it generates a
    "next time" to move."""
    def __init__(self, time, pos):
        Event.__init__(self, time)
        # Start time is stored to measure time spent crossing at the end 
        self.record = [time]
        self.pos = pos
        
    def run(self, experiment):
        # If at the end, store results and remove from list
        if self.pos + experiment.settings.fatness +1 >= len(experiment.positions):
            self.record.append(self.time)
            experiment.results.append(self.record)
            experiment.positions[self.pos].runner = None
            return
        # Record the time if we are at a recorder
        if experiment.positions[self.pos].recorder:
            self.record.append(self.time)
        # Move forward
        experiment.positions[self.pos].runner = None
        self.pos += 1
        experiment.positions[self.pos].runner = self
        # Get new time
        self.time = self.nextTime(experiment, self.time + nextRandomTime(experiment.settings.rate), experiment.positions[self.pos + experiment.settings.fatness].runner)
        # Requeue
        heappush(experiment.heap, self)
        
    def __str__(self):
        return "Runner(position=" + str(self.pos) + ", time=" + str(self.time) + ")"
    
    def nextTime(self, experiment, time, next):
        """ Generate a time to move next, given a current time."""
        settings = experiment.settings
        endpause = experiment.positions[self.pos].endOfPause(time)
        if endpause != time: # Current time is paused
            if settings.wait_pause == 1:
                time = endpause
                time += nextRandomTime(settings.rate)
            else:
                while time < endpause:
                    time += nextRandomTime(settings.rate)
            return self.nextTime(experiment, time, next)
        elif (next is not None) and (next.time > time): # Current time is blocked
            if settings.wait_block == 1:
                time = next.time
                time += nextRandomTime(settings.rate)
            else:
                while time < next.time:
                    time += nextRandomTime(settings.rate)
            return self.nextTime(experiment, time, next)
        else:
            return time
        
class Factory(Event):
    """ Creates Runners at the start of the RNA polymeraze """
    def __init__(self, maxcount):
        Event.__init__(self, 0)
        self.maxcount = maxcount
    
    def run(self, experiment):
        # If there not room, wait to try again. Otherwise, make a new runner
        for position in experiment.positions[0:experiment.settings.fatness]:
            if position.runner is not None:
                if experiment.settings.wait_block == 1:
                    self.time = position.runner.time
                    self.time += nextRandomTime(experiment.settings.rate * experiment.density)
                else:
                    while self.time < position.runner.time:
                        self.time += nextRandomTime(experiment.settings.rate * experiment.density)
                
                heappush(experiment.heap, self)
                return
                
        # Generate a new runner, and give it a proper time to move
        new = Runner(self.time, 0)
        new.time = new.nextTime(experiment, new.time + nextRandomTime(experiment.settings.rate), experiment.positions[new.pos + experiment.settings.fatness].runner)
        experiment.positions[0].runner = new
        heappush(experiment.heap, new)
        self.maxcount -= 1
        if self.maxcount > 0:
            heappush(experiment.heap, self)
            
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
        heappush(experiment.heap, self)
