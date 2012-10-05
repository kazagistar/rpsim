#!/usr/bin/python
class Event:
    """ Events are placed in a heap, sorted in decreasing order according to 
    what time they fire. They must all implement a run function, which is reponsible 
    for processing them and placing them back in the queue with a new, higher time. """
    def __init__(self, time):
        self.time = time
        
    def __cmp__(self, other):
        if self.time < other.time:
            return -1
        elif self.time == other.time:
            return 0
        else: #self.time > other.time
            return 1
        
    def run(self, experiment):
        raise NotImplementedError("Must extend event class to use")
        
    # Implementing a __str__ is recommended for debugging
