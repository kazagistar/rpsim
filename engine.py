#!/usr/bin/python
from multiprocessing import Pool
from settings import loadSettings
from experiment import Experiment
import traceback, sys, os

def runexperiment(number, settings, resultsfolder):
    resultsfile = os.path.join(resultsfolder, str(number))
    if os.path.isfile(resultsfile):
        print "Skipping " + str(number)
        return
    print "Starting " + str(number)
    try:
        exp = Experiment(settings)
        exp.run()
        writeResults(exp.results, resultsfile)
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
        sfile = sys.argv[1]
        rfile = sys.argv[2]
        print "Settings file: " + sfile
        print "Results folder: " + rfile
    except IndexError:
        print "Bad parameters, should be 'engine.py settingsfile resultsfolder'"
        quit()

    # Generate variables
    settings = loadSettings(settingsfile)
    pool = Pool()

    # Queue all simulations
    for number in xrange(settings.runs):
        pool.apply_async(runexperiment, [number, settings, resultsfile])

    # Wait for all simulations to terminate
    pool.close()
    pool.join()
    print "Experiments concluded :)"
