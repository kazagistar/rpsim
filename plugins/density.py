from plugin import event
import csv, os

# Density is recorded as the "sum of time particles spent at each position during a timestep"
# Density record is what is actually saved
# while entry time is used to compute how long it stayed

@event('simulation_start')
def init_zero_density(simulation, **_):
    simulation.density_record = [0] * settings['size']
    simulation.density_entry_time = [0] * settings['size']

@event('particle_start')
def first_position(time, simulation, **_):
    simulation.density_entry_time[0] = time

@event('particle_move')
def track_on_recorders(particle, time, simulation, **_):
	pos = particle.position
	simulation.density_record[pos-1] += time - simulation.density_entry_time[pos-1]
	simulation.density_entry_time[pos] = time

@event('particle_end')
def track_exit(particle, time, simulation, **_):
	last = particle.position - 1
    simulation.density_record[last] += time - simulation.density_entry_time[last]

# Record the density at regular intervals
class DensityMeasurement(DESEvent):
    def event(self, time, simulation):
        self.time += simulation['recording_frequency']
        # TODO




@event('simulation_end')
def print_times(simulation, **_):
    outfile = "flux{0}.csv".format(simulation.number)
    outfile = os.path.join(simulation.settings['output'], outfile)
    with open(outfile, "w") as out:
        csv.writer(out).writerows(simulation.flux_record)