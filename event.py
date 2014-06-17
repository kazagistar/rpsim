from collections import deque
import random
from math import log


class UnifiedEventSelector:
    def __init__(self, start_time=0):
        self.priority = EventQueue()
        self.kmcs = KMCSelector()
        self.time = start_time

        self.add_kmce = self.kmcs.add_event

        self.add_dese = self.priority.push


    def __iter__(self):
        return self

    def __next__(self):
        if self.kmcs.noActive():
            if len(self.priority) == 0:
                raise StopIteration()
            else:
                return self.priority.pop()
        next_time = random.expovariate(self.kmcs.sum) + self.time
        if len(self.priority) != 0:
            _, cutoff = self.priority.peek()
            if next_time > cutoff:
                self.time = cutoff
                return self.priority.pop()
        self.time = next_time
        return self.kmcs.next(), next_time


from heapq import heappush, heappop

class DESEvent(object):
    """ Superclass for events. When rate is updated, it automatically adjusts the rate in its container KMCSelector """
    def __init__(self, event=None, time=0):
        self._event = event
        # Tech debt, verify time not changed when it should not be.
        self.time = time

    def event(self, time, simulation):
        pass

class EventQueue:
    def __init__(self):
        self._heap = []
        self._count = 0

    def push(self, event):
        self._count += 1
        heappush(self._heap, (event.time, self._count, event))

    def pop(self):
        time, _, event = heappop(self._heap)
        return event, time

    def peek(self):
        time, _, event = self._heap[0]
        return event, time

    def __len__(self):
        return len(self._heap)

    def __str__(self):
        return "EventQueue({0})".format(','.join(map(str, self._heap)))


class KMCEvent(object):
    """ Superclass for events. When rate is updated, it automatically adjusts the rate in its container KMCSelector """
    def __init__(self, event=None):
        self._event = event
        self._selector = None
        self._rate = 0

    @property
    def rate(self):
        return self._rate
    @rate.setter
    def rate(self, new):
        change = new - self._rate
        self._rate = new
        if self._selector:
            self._selector.update(self, change)

    def __str__(self):
        return "MKCEvent(rate={0}, event={1}".format(str(self.rate), self._event)

class KMCSelector:
    def __init__(self):
        self.active = []
        self.max = 0
        self.sum = 0

    def add_event(self, event):
        event._selector = self
        self.sum += event.rate
        self.max = max(self.max, event.rate)
        self.active.append(event)


    def update(self, event, change):
        self.max = max(self.max, event._rate)
        self.sum += change

    def next(self):
        while True:
            index = random.randrange(len(self.active))
            event = self.active[index]
            target = random.uniform(0.0, self.max)
            if event.rate >= target:
                self.active[index] = self.active[-1]
                self.active.pop()
                event._selector = None
                self.sum -= event.rate
                return event

    def noActive(self):
        return self.sum == 0.0 or len(self.active) == 0

    def __str__(self):
        return "KMCSelector(max={0}, sum={1}, active={2})".format(
            str(self.max), str(self.sum), str(list(map(str, self.active))))