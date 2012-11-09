#!/usr/bin/python
from event import Factory, Repeater, Position
from heapdes import DiscreteEventSimulator

class Experiment(DiscreteEventSimulator):
    """ This class represents each experimental run """
    def __init__(self, settings):
        self.heap = []
        self.positions = [Position(self) for number in xrange(settings.size)]
        self.settings = settings
        self.results = []
        # Create the factory for runners
        self.pushEvent(Factory(settings.count))
