#!/usr/bin/python
import scipy.io as sio
import os, sys

from settings import load
from experiment import ExperimentSet
from results import writeResults

def splice_pauses(settings, matlab_file, matlab_variable):
    pauses = sio.loadmat(matlab_file)[matlab_variable]
    pauses = list((int(position), start, start + length)
              for position, start, length in pauses)
    settings["pauses"] = pauses

if __name__ == "__main__":
    # Read arguments
    try:
        settingsFile = sys.argv[1]
        resultsFolder = sys.argv[2]
        matlab_file = sys.argv[3]
        matlab_variable = sys.argv[4]
        print "Settings file: " + settingsFile
        print "Results folder: " + resultsFolder
        print "Pauses stored in %s -> [%s]" % (matlab_file, matlab_variable)
    except IndexError:
        print "Bad parameters, should be 'engine.py settings_file results_folder matlab_file matlab_variable'"
        print "e.g. 'python load_pauses.py compare.json compare_results Smatrices.mat S1'"
        quit()

    # Generate variables
    settings = load(settingsFile)
    splice_pauses(settings, matlab_file, matlab_variable)
    print settings["pauses"]

    if not os.path.exists(resultsFolder):
        os.makedirs(resultsFolder)

    # Create and run the experiment
    experiments = ExperimentSet(settings, resultsFolder)
    experiments.run()

    print "Experiments concluded :)"
