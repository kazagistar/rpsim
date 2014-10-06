from plugin import event
import random
import os, csv

@event
def simulation_start(simulation, **_):
    simulation.pause_record = []

@event
def particle_rate_update(simulation, particle, **_):
    try:
        if particle.pause_start:
            particle.rate /= simulation.settings["pause_beta_slowdown"]
    except AttributeError as e:
        # Ugh... unfortunately, particle rate update is called before particle start
        # Thus, this will happen at exactly the first update only
        # so here is where we initialize "starting particle paused status"
        assert e.args[0] == "'Particle' object has no attribute 'pause_start'"
        if random.random() < simulation.settings["pause_frequency"]:
            particle.pause_start = simulation.time
            particle.rate /= simulation.settings["pause_beta_slowdown"]
        else:
            particle.pause_start = None

@event
def particle_move(particle, time, simulation, **_):
    if particle.pause_start:
        simulation.pause_record.append((particle.position - 1, particle.pause_start, time))
    if random.random() < simulation.settings["pause_frequency"]:
        particle.pause_start = time
    else:
        particle.pause_start = None

@event
def simulation_end(simulation, **_):
    outfile = "pauses{0}.csv".format(simulation.number)
    outfile = os.path.join(simulation.settings['output'], outfile)
    with open(outfile, "w") as out:
        csv.writer(out).writerows(simulation.pause_record)
