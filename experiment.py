#!/usr/bin/python
from event import Factory, Repeater, Position
from heapq import heappush, heappop

class Experiment:
    """ This class represents each experimental run """
    def __init__(self, settings, density):
        self.density = density
        self.heap = []
        self.positions = [Position(self) for number in xrange(settings.size)]
        self.settings = settings
        self.results = []
        # Create the factory for runners
        heappush(self.heap, Factory(settings.count))
        # Add pauses to the positions
        for pause in self.settings.pauses:
            self.positions[pause[0]].pauses.append(pause[1:])
        # Set the recorder properties
        for time in settings.recorders:
            self.positions[time].recorder = True

    def addRepeater(self, function, timer):
        heappush(self.heap, Repeater(function, timer))
    
    def run(self):
        while len(self.results) < self.settings.count:
            event = heappop(self.heap)
            if self.settings.debug:
                print str(self) + str(event)
            event.run(self)
        return self.results
            
    def __str__(self):
        rtrn = ""
        for item in self.positions:
            if None is item.runner:
                rtrn += "-"
            else:
                rtrn += "O"
        return rtrn
