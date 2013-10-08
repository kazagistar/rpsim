""" Simple plugin architecture

 .. moduleauthor Jakub Gedeon

To create plugin listeners, just call plugin("plugin_name"). Then, when
you use the @event decorator on a method, that method will be called
whenever the event corresponding to its function name is triggered.

To use plugins, create a new plugin set by passing in the names of the
plugins you want to use {a = PluginSet("foo", "bar", "plugin_name")} and
then trigger them like {a.trigger(event="name", baz="whatever")}
"""
from functools import wraps
from collections import defaultdict
from re import match

PLUGIN_DIR = "plugins"

_plugins = defaultdict(lambda: defaultdict(list))
_events = None

def plugin(name):
    """ Start recording event listeners under a plugin name """
    global _events
    _events = _plugins[name]

def event(func):
    """ Decorator that makes a function listen for an event (whatever it
    is named)
    
    MAKE SURE YOU ACCEPT KWARGS AND **_ ONLY!!!
    """
    _events[func.__name__].append(func)
    return func

class PluginSet:
    def __init__(self, *args):
        """ Load a set of plugins passed in as strings """
        self.events = defaultdict(list)
        for plugin in args:
            for event, function_list in _plugins[plugin].items():
                self.events[event].extend(function_list)

    def trigger(self, event, **kwargs):
        """ Pass the kwargs to all the event listeners which are registered
        to listen for the event parameter """
        for listener in self.events[event]:
            listener(event=event, **kwargs)


# Try to load all plugins from the plugin folder
import os
for filename in os.listdir(PLUGIN_DIR):
    if match(r'\.py$', filename):
        __import__("{}.{}".format(PLUGIN_DIR, filename[:-3]))
