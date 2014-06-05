#!/usr/bin/python
import scipy.io as sio
import os, sys

from settings import load
from experiment import ExperimentSet

def splice_pauses(settings, matlab_file, matlab_variable):
    pauses = sio.loadmat(matlab_file)[matlab_variable]
    pauses = list((int(position) - 1, start, start + length)
              for position, start, length in pauses)
    settings["pauses"] = pauses

if __name__ == "__main__":
    # Read arguments
    try:
        settingsFile = sys.argv[1]
        matlab_file = sys.argv[2]
        matlab_variable = sys.argv[3]
        print "Settings file: " + settingsFile
        print "Pauses stored in %s -> [%s]" % (matlab_file, matlab_variable)
    except IndexError:
        print "Bad parameters, should be 'load_pauses.py settings_file matlab_file matlab_variable'"
        print "e.g. 'python load_pauses.py compare.json Smatrices.mat S1'"
        quit()

    # Generate variables
    settings = load(settingsFile)
    splice_pauses(settings, matlab_file, matlab_variable)
    print settings["pauses"]


    # Create and run the experiment
    experiments = ExperimentSet(settings)
    experiments.run()

    print("Experiments concluded :)")
