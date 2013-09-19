#!/usr/bin/python
from settings import load
from experiment import ExperimentSet
import traceback, sys, os

if __name__ == "__main__":
    # Read arguments
    try:
        settingsfile = sys.argv[1]
        print "Settings file: " + settingsfile
    except IndexError:
        print "Bad parameters, should be 'python engine.py settingsfile'"
        quit()

    # Generate variables
    settings = load(settingsfile)

    # Create and run the experiment
    experiments = ExperimentSet(settings)
    experiments.run()
    
    print "Experiments concluded :)"
