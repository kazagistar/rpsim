from collections import deque
import random
from math import log


class UnifiedEventSelector:
    def __init__(self, start_time=0):
        self.priority = EventQueue()
        self.generators = []
        self.instant = deque()
        self.time = start_time

    def queue_event(self, time, event, params):
        self.priority.push(time, event, params)

    def add_generator(self, generator):
        self.generators.append(generator)

    def instant_event(self, event, params):
        self.instant.append((event, params))

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.instant) != 0:
            event, params = self.instant.popleft()
            return self.time, event, params

        if len(self.generators) > 0:
            rates, events, params = map(list, (zip(*(generator.next() for generator in self.generators))))
            total_rate = sum(rates)
        else:
            total_rate = 0
        if total_rate == 0:
            if len(self.priority) == 0:
                raise StopIteration("No more events")
            else:
                return self.priority.pop()

        next_time = random.expovariate(total_rate) + self.time
        if len(self.priority) != 0:
            cutoff = self.priority.peek()
            if next_time > cutoff:
                self.time = cutoff
                return self.priority.pop()
        # find which generator should have actually fired
        choice = random.uniform(0.0, total_rate)
        border = 0
        for index, rate in enumerate(rates):
            border += rate
            if border >= choice:
                self.time = next_time
                return next_time, events[index], params[index]

UnifiedEventSelector.next = UnifiedEventSelector.__next__


from heapq import heappush, heappop

class EventQueue:
    def __init__(self):
        self._heap = []
        self._index = 0

    def push(self, time, event, params):
        heappush(self._heap, (time, self._index, event, params))
        self._index += 1

    def pop(self):
        time, _, event, params = heappop(self._heap)
        return time, event, params

    def peek(self):
        return self._heap[0][0]

    def __len__(self):
        return len(self._heap)