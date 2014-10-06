from event import UnifiedEventSelector, DESEvent
from plugin import event, PluginSet
import random


class Simulation(object):
    def __init__(self, settings, number):
        self.plugins = PluginSet(*settings['plugins'])
        self.events = UnifiedEventSelector()
        self.settings = settings
        self.running = False
        self.number = number

        self.add_kmce = self.events.add_kmce
        self.add_dese = self.events.add_dese

    def run(self):
        random.seed((self.settings['seed'], self.number))
        self.add_dese(SimStart(time=0.0))
        self.add_dese(SimEnd(time=self.settings['time']))
        self.running = True
        try:
            while self.running:
                # print(self.events.kmcs)
                event, self.time = self.events.next()
                # print(event)
                event.event(self.time, self)
        except StopIteration:
            pass


class SimStart(DESEvent):
    def event(self, time, simulation):
        simulation.plugins.trigger(event="simulation_start", time=time, simulation=simulation)


class SimEnd(DESEvent):
    def event(self, time, simulation):
        simulation.plugins.trigger(event="simulation_end", time=time, simulation=simulation)
        simulation.running = False
