from plugin import event

from event import DESEvent
from time import clock


class Ticker(DESEvent):
    def __init__(self, update_time):
        super().__init__()
        self.start = clock()
        self.update_time = update_time

    def event(self, time, simulation):
        print("Simulation time {0} at ({1})".format(time, clock() - self.start))
        self.time += self.update_time
        simulation.add_dese(self)


@event
def simulation_start(simulation=None, **_):
    simulation.add_dese(Ticker(update_time=1))