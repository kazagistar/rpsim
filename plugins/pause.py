from plugin import event
import random
import os, csv

@event('simulation_start')
def initialize_recording(simulation, **_):
    simulation.pause_record = []

@event('particle_start')
def track_entry(particle, time, simulation, **_):
    particle.pause_start = None
    if random.random() < simulation.settings["pause_frequency"]:
        particle.rate /= simulation.settings["pause_beta_slowdown"]
        particle.pause_start = time

@event('particle_move')
def track_entry(particle, time, simulation, **_):    
    if particle.pause_start:
        simulation.pause_record.append((particle.position - 1, particle.pause_start, time))
        particle.pause_start = None
    if random.random() < simulation.settings["pause_frequency"]:
        particle.rate /= simulation.settings["pause_beta_slowdown"]
        particle.pause_start = time

@event('simulation_end')
def print_times(simulation, **_):
    outfile = "pauses{0}.csv".format(simulation.number)
    outfile = os.path.join(simulation.settings['output'], outfile)
    with open(outfile, "w") as out:
        csv.writer(out).writerows(simulation.pause_record)
