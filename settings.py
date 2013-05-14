#!/usr/bin/python
import json

def load(filename, settings=None):
    """
    Loads a file of settings into a settings dictionary, or a set of default settings if none are provided.
    
    The settings are stored in JSON format. All are optional (default values in {})
    
    size = (integer) the number of positions in each simulation {1}
    time = (float) how long to run the simulation {1}
    fatness = (integer) how wide each runner is {1}
    runs = (integer) how many times to run each experiment with the same parameters {1}
    alpha = (float) insertion rate, or how fast runners should be added into the simulation {1.0}
    beta = (float) flow rate, or how fast runners should move from position to positon {1.0}
    recording_frequency = (float) how often the density is measured and stored {1.0}
    pauses = a list [] of tuples representing pauses in the form (position, starttime, endtime) {[]}
    recorders = a list [] of locations at which to record data, measured by when a runner leaves the space (start times are recorded automatically) {[]} 
    debug = (integer) the debug level {0}
    """
    # Load default settings if needed
    if settings == None:
        settings = {
        	"size":10,
        	"time":1,
            "fatness": 1,
            "runs": 1,
            "alpha": 1.0,
            "beta": 1.0,
            "recording_frequency": 1.0,
            "pauses": [],
            "recorders": [],
            "debug": 0
        }

    # Override any settings stored in the file
    with open(filename) as f:
        datafile = json.load(f)
        settings.update(datafile)
    
    return settings
