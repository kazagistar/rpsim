from event import UnifiedEventSelector, DESEvent
from plugin import event, PluginSet


class Simulation:
	def __init__(self, settings, number):
		self.plugins = PluginSet(*settings['plugins'])
		self.events = UnifiedEventSelector()
		self.settings = settings
		self.running = False
		self.number = number

		self.add_kmce = self.events.add_kmce
		self.add_dese = self.events.add_dese

	def run(self):
		self.add_dese(DESEvent(event='simulation_start', time=0.0))
		self.add_dese(SimEnd(time=self.settings['time']))
		self.running = True

		try:
			while self.running:
				print(str(self.events.kmcs))
				print(str(self.events.priority))
				event, time = next(self.events)
				event.event(time, self)
				self.plugins.trigger(event, time, self)
		except StopIteration:
			pass

class SimEnd(DESEvent):
	def __init__(self, time):
		super().__init__(event='simulation_end', time=time)

	def event(self, time, simulation):
		simulation.running = False