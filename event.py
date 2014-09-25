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
        if self.kmcs.event_sum() == 0:
            if len(self.priority) == 0:
                raise StopIteration()
            else:
                _, self.time = self.priority.peek()
                return self.priority.pop()
        next_time = random.expovariate(self.kmcs.total) + self.time
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

    def __init__(self, time=0):
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

    def __init__(self):
        self._selector = None
        self._rate = 0

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, value):
        self._rate = value


    def __str__(self):
        return "{0}(rate={1})".format(self.__class__.__name__, self.rate)


class KMCSelector:
    def __init__(self):
        self.active = []

    def add_event(self, event):
        self.active.append(event)
        event._selector = self

    def event_sum(self):
        self.total = 0.0
        for event in self.active:
            self.total += event._rate
        return self.total

    def next(self):
        # Pick the event randomly
        target = random.uniform(0.0, self.total)
        for index, event in enumerate(self.active):
            target -= event.rate
            if target <= 0.0:
                self.active[index], self.active[-1] = self.active[-1], self.active[index]
                return self.active.pop()

    def __str__(self):
        return "KMCSelector(active={0})".format(
            str(sorted(list(map(str, self.active)))))
