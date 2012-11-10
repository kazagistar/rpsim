#!/usr/bin/python
import json

def loadSettings(filename, settings=None)
    """
    Loads a file of settings into a settings dictionary, or a set of default settings if none are provided.
    
    The settings are stored in JSON format... all are optional (default values in {})
    
    count = (integer) how many RNA polymeraze "runners" to send {1}
    fatness = (integer) how wide each runner is... affects maximum density {1}
    runs = (integer) how many times to run each experiment with the same parameters {1}
    rate = (float) beta, flow rate, or how fast runners should move along the strand {1.0}
    density = (float) a fraction of rate, which determines how quickly runners should start.
        For example, 0.5 means runners will start at half the rate at which they travel accross {1.0}
    debug = (integer) the debug level {0}
    
    if a rna polymerase cannot do an action because something is stopping it, these variable determine what strategy to use
        1 = dont move until (when the blocking thing ends) + (rate()) ie the "wait until clear" strategy
        0 = keep trying to move by generating new move times until after the block is clear ie the "retry until clear" strategy
    wait_block = which strategy to use when blocked by an RNA polymeraze
    wait_pause = which stragegy to use when the current position is paused
    
    pauses = a list [] of tuples representing pauses in the form (position, starttime, endtime)
    recorders = a list [] of locations at which to record data, measured by when a runner leaves the space
    (starting times are recorded automatically)
    
    While it might seem that there should be a "size", only recorded data is really important, so the size is the position of the last recorder.
    """
    # Load default settings if needed
    if settings == None:
        settings = {
            "count": 1,
            "fatness": 1,
            "runs": 1,
            "rate": 1.0,
            "density": 1.0,
            "debug": 0,
            "wait_block": 0,
            "wait_pause": 0,
            "pauses": [],
            "recorders": []
        }

    # Override any settings stored in the file
    with open(filename):
        datafile = json.load(f)
        settings.update(datafile)
    
    # Convenience variable
    settings["size"] = max(self.recorders) + 1
    
    return settings
