#!/usr/bin/python
from multiprocessing import Pool
from settings import loadSettings
from experiment import Experiment
from results import writeResults
import traceback, sys, os

def runexperiment(number, settings, resultsFolder):
    resultsfile = os.path.join(resultsFolder, str(number))
    if os.path.isfile(resultsfile):
        print "Skipping " + str(number)
        return
    print "Starting " + str(number)
    try:
        exp = Experiment(settings)
        exp.run()
        writeResults(exp.results, resultsFolder)
        print "Finished " + str(number)
    except:
        # Unfortunately, multiprocessing silently eats exceptions
        # Thus, we have to print them manually
        # This is a python bug, and might be fixed in later versions
        print "Error in " + str(number)
        traceback.print_exc(file=sys.stdout)


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
    settings = loadSettings(settingsFile)
    pool = Pool()

    # Queue all simulations
    for number in xrange(settings.runs):
        pool.apply_async(runexperiment, [number, settings, resultsFolder])

    # Wait for all simulations to terminate
    pool.close()
    pool.join()
    print "Experiments concluded :)"
