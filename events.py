from functools import wraps
from collections import defaultdict

_events = defaultdict(set)

def event(func):
	_events[func.__name__].add(func)
	return func

def trigger(event, **kwargs):
	for listener in _events[event]:
		listener(event=event, **kwargs)

@event
def dostuff(event, stuff, **_):
	print(stuff, "yay")
	
trigger(event="dostuff", stuff="whatever", fail="sdfasd")

