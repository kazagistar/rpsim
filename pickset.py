from itertools import *
import operator

# From itertools recipies
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

class PickSet(object):
    " Put objects into a set, then use an RNG to pick items weighted by a monoid "
    bwidth=2
    mappend=operator.add
    mzero=0

    def __init__(self, data=[]):
        self.ids = {}
        self.data = list(data)
        if self.data == []:
            self.caches = [[self.mzero]]
            return
        self.caches = []
        for ix, item in enumerate(self.data):
            self.ids[id(item)] = ix
        layer = [measure(item) for item in self.data]
        while True:
            grouped = list(grouper(layer, self.bwidth, self.mzero))
            layer = [reduce(self.mappend, g) for g in grouped]
            self.caches.append(layer)
            if len(layer) == 1:
                break

    def measure(self, m):
        if m.__measure__:
            return m.__measure__()
        else:
            return m

    def __repr__(self):
        return "PickSet(data={0}, caches={1}, ids={2})".format(self.data, self.caches, self.ids)
        
    def add(self, item):
        " Add item to set, O(log(n)) "
        ix = len(self.data)
        assert not (id(item) in self.ids), "PickSet implementation requires uniqueness"
        self.data.append(item)
        self.ids[id(item)] = ix
        self._update(ix)
    
    def _children(self, index, layer):
        first = index * self.bwidth
        last = min(first + self.bwidth, len(layer))
        return layer[first:last]
        
    def _update(self, index):
        index /= self.bwidth
        updated = [self.measure(item) for item in self._children(index, self.data)]
        for layer in self.caches:
            if len(updated) == 0:
                layer.pop()
            else:
                val = reduce(self.mappend, updated, self.mzero)
                if index == len(layer):
                    layer.append(val)
                else:
                    layer[index] = val
            index /= self.bwidth
            updated = self._children(index, layer)
        if len(self.caches[-1]) > 1:
            self.caches.append([self.mappend(layer[0], layer[1])])
        elif len(self.caches[-1]) < 1:
            self.caches.pop()
        if len(self.caches) == 0:
            self.caches = [[self.mzero]]
    
    def swap(self, old, new):
        " Change item for another (or just update item measure) O(log(n)) "
        assert id(old) in self.ids, "Accessing nonexistant event"
        ix = self.ids.pop(id(old))
        self.data[ix] = new
        self.ids[id(new)] = ix
        self._update(ix)

    def delete(self, old):
        " Remove item from set O(log(n)) "
        assert id(old) in self.ids, "Accessing nonexistant event"
        ix = self.ids[id(old)]
        endix = len(self.data) - 1
        self.ids[id(self.data[endix])] = ix
        self.data[ix] = self.data[endix]
        self.data.pop()
        del self.ids[id(old)]
        self._update(ix)
        self._update(endix)
        
    def pick(self, random):
        " Given a random number, pick an item P(log(n)) "
        ix = 0
        total = 0
        for layer in reversed(self.caches):
            while True:
                if ix >= len(layer):
                    raise Exception("Could not pick item")
                if total + layer[ix] > random:
                    ix *= self.bwidth
                    break
                ix += 1
                total += layer[ix]
        while True:
            meas = self.measure(self.data[ix])
            if ix >= len(self.data):
                raise Exception("Could not pick item")
            if total + meas > random:
                return self.data[ix]
            ix += 1
            total += meas
