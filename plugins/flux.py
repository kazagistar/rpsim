from plugin import event

@event('simulation_start')
def print_times(simulation=None, **_):
	simulation.flux_record = []

@event('particle_start')
def track_entry(particle=None, time=None, **_):
	particle.flux_start_time = time

@event('particle_end')
def track_exit(particle=None, time=None, simulation=None, **_):
	simulation.flux_record.append((particle.flux_start_time, time))

@event('simulation_end')
def print_times(simulation=None, **_):
	print(simulation.flux_record)