""" Simple plugin architecture

 .. moduleauthor Jakub Gedeon

To create plugin listeners, just call plugin("plugin_name"). Then, when
you use the @event decorator on a method, that method will be called
whenever the event corresponding to its function name is triggered.

To use plugins, create a new plugin set by passing in the names of the
plugins you want to use {a = PluginSet("foo", "bar", "plugin_name")} and
then trigger them like {a.trigger(event="name", baz="whatever")}
"""
from collections import defaultdict
from importlib import import_module

PLUGIN_DIR = "plugins"

def event(func):
    """ Decorator that makes a function listen for an event (whatever it
    is named)
    
    MAKE SURE YOU ACCEPT KWARGS AND **_ ONLY!!!
    """
    def register(method):
        # First, grab the eventlist from the function's module (or create one if none exists)
        namespace = method.__globals__
        namespace['__EVENTS__'] = eventlist = namespace.get('__EVENTS__', defaultdict(list))
        # (Mild hack... name is defined in the calling context)
        eventlist[name].append(method)
        return method
        
    if callable(func):
        name = func.__name__
        return register(func)
    else:
        name = func
        return register


class PluginSet:
    _plugin_path = "plugins."
    def __init__(self, *args):
        """ Load a set of plugins passed in as strings """
        self.events = defaultdict(list)
        for name in args:
            plugin = import_module(self._plugin_path + name)
            for event, function_list in plugin.__EVENTS__.items():
                self.events[event].extend(function_list)

    def trigger(self, event, time, simulation):
        """ Pass the kwargs to all the event listeners which are registered
        to listen for the event parameter """
        for listener in self.events[event._event]:
            listener(event, time, simulation)
