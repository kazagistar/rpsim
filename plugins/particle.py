from plugin import event
from ratearray import RateArray

@event
def simulation_start(settings, **_):
	movement = RateArray(100)