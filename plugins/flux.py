from plugin import event
import csv, os

@event('simulation_start')
def print_times(simulation, **_):
    simulation.flux_record = []


@event('particle_start')
def track_entry(particle, time, **_):
    particle.flux_start_time = time


@event('particle_end')
def track_exit(particle, time, simulation, **_):
    simulation.flux_record.append((particle.flux_start_time, time))


@event('simulation_end')
def print_times(simulation, **_):
    outfile = "flux{0}.csv".format(simulation.number)
    outfile = os.path.join(simulation.settings['output'], outfile)
    with open(outfile, "w") as out:
        csv.writer(out).writerows(simulation.flux_record)