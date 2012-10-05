#!/usr/bin/python
class Position:
    """ struct for holding data about positions... determines how next time is generated """
    def __init__(self, number):
        self.runner = None
        # Will contain 2-tuples with a start time and an end time
        self.pauses = []
        self.recorder = False
