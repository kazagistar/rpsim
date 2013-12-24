import random

class ActiveEvent:
    __slots__ = ["index", "rate"]

    def __init__(self, index, rate):
        self.index = index
        self.rate = rate


class RateArray:
    def __init__(self, event, size, params={}):
        self._index = [None] * size
        self._active = []
        self._max = 0
        self._sum = 0
        self.event = event
        self._params = params

    def __getitem__(self, key):
        index = self._index[key]
        if index:
            return self._active_rate[index]
        else:
            return 0

    def __setitem__(self, key, rate):
        index = self._index[key]
        if rate == 0:
            if not index:
                return
            else:
                self._sum -= self._active[index].rate
                self._active[index] = self._active[-1]
                moved = self._active.pop()
                self._index[moved.index] = index
                self._index[key] = None
                return
        else:
            self._max = max(self._max, rate)
            if index:
                event = self._active[index]
                self._sum += rate - event.rate 
                event.rate = rate
                return
            else:
                self._index[key] = len(self._active)
                self._active.append(ActiveEvent(key, rate))
                self._sum += rate

    def next(self):
        while True:
            event = random.choice(self._active)
            target = random.uniform(0.0, self._max)
            if event.rate >= target:
                return self._sum, self.event, {"index": event.index}.update(self._params)
