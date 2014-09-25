#!/usr/bin/python
from settings import load
from simulation import Simulation
import sys, os, traceback

# Function to execute simulation runs in parallel, with manual exception handling
def sim_run(count):
    try:
        sim = Simulation(settings, count)
        sim.run()
        return count
    except Exception as e:
        print("Exception in run {0}".format(count))
        traceback.print_exc()
        print()
        raise e


if __name__ == "__main__":
    # Read arguments
    try:
        settingsFile = sys.argv[1]
    except IndexError:
        print("Bad parameters, should be 'engine.py settingsfile'")
        quit()

    # Generate variables
    settings = load(settingsFile)

    # Default "simple" run mode
    if settings['cores'] == 1:
        for count in range(settings['runs']):
            sim = Simulation(settings, count)
            sim.run()
        print("Simulations concluded :)")
        exit()

    # Multiprocess run mode
    # Most recent run is stored in a "finished" file

    from multiprocessing import Pool
    pool = Pool(processes=settings['cores'])

    # Fetching number of previously completed runs
    lockfile = os.path.join(settings['output'], 'finshed.lock')
    try:
        with open(lockfile, 'r') as f:
            count, shash = f.read().split(' ')
            # check if the settings have changed at all
            if shash == settings.hash():
                start = int(count) + 1
            else:
                start = 0
    except FileNotFoundError:
        start = 0
    except ValueError:
        start = 0

    # Iterate over remaining runs
    finished = pool.imap(sim_run, range(start, settings['runs']))

    # Record finished runs back into lock file
    for counted in finished:
        with open(lockfile, 'w') as f:
            f.write(str(counted) + " " + settings.hash())
