#!/usr/bin/python
from settings import load
from experiment import ExperimentSet
import traceback, sys, os

if __name__ == "__main__":
    # Read arguments
    try:
        settingsFile = sys.argv[1]
        resultsFolder = sys.argv[2]
        print "Settings file: " + settingsFile
        print "Results folder: " + resultsFolder
    except IndexError:
        print "Bad parameters, should be 'engine.py settingsfile resultsfolder'"
        quit()

    # Generate variables
    settings = load(settingsFile)

    # Create and run the experiment
    experiments = ExperimentSet(settings, resultsFolder)
    for experiment in experiments.experiments:
    	print len(experiment.positions)
    experiments.run()
    
    print "Experiments concluded :)"
