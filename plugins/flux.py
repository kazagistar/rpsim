from plugin import event
import csv

@event('simulation_start')
def print_times(simulation, **_):
    simulation.flux_record = []


@event('particle_start')
def track_entry(particle, time, **_):
    particle.flux_start_time = time

@event('particle_move')
def track_at_recorders(particle, time, **_)


@event('particle_end')
def track_exit(particle, time, simulation, **_):
    simulation.flux_record.append((particle.flux_start_time, time))


@event('simulation_end')
def print_times(simulation=None, **_):
    outfile = "flux{1}.csv".format(simulation.number)
    with open(outfile, "w") as out:
        csv.writer(out).writerows(simulation.flux_record)