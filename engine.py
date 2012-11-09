#!/usr/bin/python
from multiprocessing import Pool
from settings import loadSettings
from experiment import Experiment
from results import Results
import traceback, sys

def runexperiment(number, settings, resultsfile):
    print "Starting " + str(number)
    try:
        exp = Experiment(settings)
        exp.run()
        Results(resultsfile).add(exp.results, density, number)
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
        print "Results file: " + rfile
    except IndexError:
        print "Bad parameters, should be 'engine.py settingsfile resultsfile'"
        quit()

    # Generate variables
    settings = loadSettings(settingsfile)
    pool = Pool()

    # Queue all simulations
    for density in settings.densities:
        for number in xrange(settings.runs):
            pool.apply_async(runexperiment, [density, number, settings, resultsfile])

    # Wait for all simulations to terminate
    pool.close()
    pool.join()
    print "Experiments concluded :)"
