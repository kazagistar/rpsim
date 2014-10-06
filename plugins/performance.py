from plugin import event
import os, csv
from event import DESEvent
import time as T


class Ticker(DESEvent):
    def __init__(self, update_time):
        super(Ticker, self).__init__()
        self.start_time  = T.time()
        self.update_time = update_time

    def event(self, time, simulation):
        data = (time, T.time() - self.start_time)
        print("Sim {sim.number} {time}".format(sim=simulation, time=data))
        simulation.performance_record.append(data)
        self.time += self.update_time
        simulation.add_dese(self)

@event
def simulation_start(simulation=None, **_):
    simulation.performance_record = []
    simulation.add_dese(Ticker(update_time=5.0))

@event
def simulation_end(simulation, **_):
    outfile = "performance{0}.csv".format(simulation.number)
    outfile = os.path.join(simulation.settings['output'], outfile)
    with open(outfile, "w") as out:
        csv.writer(out).writerow(('sim', 'wall'))
        csv.writer(out).writerows(simulation.performance_record)
