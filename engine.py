#!/usr/bin/python
from settings import load
from simulation import Simulation
import sys

if __name__ == "__main__":
    # Read arguments
    try:
        settingsFile = sys.argv[1]
    except IndexError:
        print("Bad parameters, should be 'engine.py settingsfile'")
        quit()

    # Generate variables
    settings = load(settingsFile)

    for count in range(settings['runs']):
        sim = Simulation(settings, count)
        sim.run()
    
    print("Simulations concluded :)")
