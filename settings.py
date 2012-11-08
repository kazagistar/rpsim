#!/usr/bin/python
import json
from multiprocessing import Lock

class Settings:
    """
    The following settings are stored in JSON format:
    
    count = (integer) how many RNA polymeraze runners to send
    fatness = (integer) how wide each runner is... affects maximum density
    runs = (integer) how many times to run each experiment with the same parameters
    debug = (boolean) should the program display debug information?
    
    wait_block = 
    wait_pause = 
    
    pauses = a list [] of tuples representing pauses in the form (position, starttime, endtime)
    densities = list [] of alpha values, or in-flow rates, as floating point numbers
    recorders = a list [] of locations at which to record data
    """
    def __init__(self, filename):
        self.filename = filename
        try:
            self.load()
        except IOError as e:
            self.reset()
            self.save()
            
    def load(self):
        """Loads all the data from the datafile"""
        # Load the data from the file
        with open(self.filename):
            data = json.load(f)
        
        # Extract individual variables
        self.count = data['count']
        self.rate = data['rate']
        self.fatness = data['fatness']
        self.runs = data['runs']
        self.debug = data['debug']
        
        self.wait_block = data['wait_block']
        self.wait_pause = data['wait_pause']
        
        # Load list forms
        
        # List of pauses in the form (position, starttime, endtime)
        self.pauses = data['pauses']
        # List of densities
        self.densities = data['densities']
        # recorders: List of integers representing points which will be measured along the path of a runner
        self.recorders = data['recorders']
        
        
    def save(self):
        """ Saves all the data to the datafile """
        data = {}
        
        # Save individual values
        data['count'] = self.count
        data['rate'] = self.rate
        data['fatness'] = self.fatness
        data['runs'] = self.runs
        data['debug'] = self.debug
        data['wait_block'] = self.wait_block
        data['wait_pause'] = self.wait_pause
        
        # Save pauses and recorders
        data['pauses'] = self.pauses
        data['densities'] = self.densities
        data['recorders'] = self.recorders
        
        data['version'] = VERSION
        
        # Save to file
        f = open(self.filename,'w')
        f.write(json.dumps(data))
        f.close()

    def reset(self):
        """ Reset to default values for testing """
        self.size = 1
        self.count = 1
        self.rate = 1
        self.fatness = 1
        self.runs = 1
        self.debug = 0
        self.wait_block = 0
        self.wait_pause = 0
        self.pauses = []
        self.densities = []
        self.recorders = []
        
    # Convenience variables
    def getSize(self):
        """ Returns the size the testing array should be to fit all the recorders """
        # + 1 because the last recorder has to have a position
        return max(self.recorders) + 1
    size = property(getSize)

