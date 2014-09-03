from plugin import event
import csv, os

@event('simulation_start')
def print_times(simulation, **_):
    simulation.flux_record = []
    simulation.flux_recorders = frozenset(simulation.settings['recorders'])

@event('particle_start')
def track_entry(particle, time, **_):
	# Store start time
    particle.flux_timings = [time]

@event('particle_end')
def track_exit(particle, time, simulation, **_):
    simulation.flux_record.append(particle.flux_timings)

@event('particle_move')
def track_on_recorders(particle, time, simulation, **_):
	if particle.position in simulation.flux_recorders:
		particle.flux_timings.append(time)

@event('simulation_end')
def print_times(simulation, **_):
    outfile = "flux{0}.csv".format(simulation.number)
    outfile = os.path.join(simulation.settings['output'], outfile)
    with open(outfile, "w") as out:
        csv.writer(out).writerows(simulation.flux_record)