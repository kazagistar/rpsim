#!/usr/bin/python
import json
from multiprocessing import Lock

VERSION = 3

class Settings:
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
        f = open(self.filename,'r')
        data = json.load(f)
        f.close()
        
        # Check versioning
        assert data['version'] == VERSION 
        
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

