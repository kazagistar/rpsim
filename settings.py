#!/usr/bin/python
import json
import os
import hashlib
import copy
from collections.abc import Mapping

class Settings(Mapping):
    """
    size = (integer) the number of positions in each simulation
    time = (float) how long to run the simulation
    base_width = (integer) the closest two particles can be next to each other
    base_width = (integer) how much of the RNA is held static by the runners, unable to twist
    runs = (integer) how many times to run each experiment with the same parameters
    alpha = (float) insertion rate, or how fast runners should be added into the simulation
    beta = (float) flow rate, or how fast runners should move from position to positon
    recording_frequency = (float) how often the density is measured and stored
    recorders = a list [] of locations at which to record particle exit data (start position also recorded)
    output = the filename you want the results to be written
    cores = number of processes that will evaluate in parallel
    seed = (integer or null) seeding value for the random number generator (set to None by default for random)
    """
    def __init__(self, settings):

        self._known = {
            "runs": 1,
            "pauses": [],
            "cores": 1,
            "debug": 0,
            "seed": None }
        self._known.update(settings)

    def __getitem__(self, key):
        assert key in self._known, "Settings must contain {0}".format(key)
        return self._known[key]

    def __iter__(self):
        self._known.__iter__()

    def __len__(self):
        self._known.__len__()

    def hash(self):
        # remove values that don't change individual sim output for the hash
        settings = copy.copy(self._known)
        del settings['cores']
        del settings['runs']
        del settings['debug']
        return hashlib.md5(json.dumps(settings, sort_keys=True).encode('utf-8')).hexdigest()
    

def load(filename, settings=None):
    with open(filename) as f:
        datafile = json.load(f)

    if not settings:
        settings = Settings(datafile)
    else:
        settings.update(datafile)
    
    if not os.path.exists(settings['output']):
        os.makedirs(settings['output'])

    return settings
