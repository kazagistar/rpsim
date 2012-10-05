#!/usr/bin/python
import matplotlib.pyplot as plt
import scipy.io as sio
import numpy as np
from settings import Settings
from math import sqrt
from results import Results
import sys

FLUX_WINDOW = 5.0
FLUX_STEP   = 0.1

def dataRaw(settings, density):
    """ Gets 2 lists from results... all the start times, and all the end times """
    results = settings.results[str(density)]
    combined = [item for sublist in results for item in sublist]
    return zip(*combined)
    
def dataFlux(data, scale):
    arrivals = sorted(data)
    # bot = lowest value of the current window
    bot = min(arrivals)
    # top = highest value of the current window
    top = bot + FLUX_WINDOW
    # window = a list of values matching the window
    window = []
    # densities = a set of tuples where x is the time and y is the density at that time
    #   this is what is returned from the function
    flux = []
    
    for time in arrivals:
        while time > top:
            # If we found the end of the window, store the window information, scaled
            flux.append(( (top + bot)/2, len(window)/(float(FLUX_WINDOW)*scale) ))
            # Set to new window, and remove old window values
            bot += FLUX_STEP
            top += FLUX_STEP
            #print "WINDOWBEFORE: " + str(window) + " : " + str(bot)
            while (len(window) is not 0) and (window[0] <= bot):
                window.pop(0)
            #print "WINDOWAFTER: " + str(window) + " : " + str(bot)
            #raw_input()
        window.append(time)
    
    return zip(*flux)
    
def dataDensity(flux, beta):
    """ The density formula... takes in the dataFlux data, and the beta (travel rate during the experiment) """
    x,y = flux
    y = map(lambda n: 0.5 * (1- sqrt(max(1-4*n/float(beta),0))),y)
    return x,y

def exportMatlab(data, filename):
    """ Stores analyzed data into a matlab file """
    # Settings, for reference
    export = {}
    export['sim_size'] = data.size
    export['sim_count'] = data.count
    export['sim_rate'] = data.rate
    export['sim_fatness'] = data.fatness
    export['sim_runs'] = data.runs
    
    # Pauses
    pos, start, end = zip(*data.pauses)
    export['sim_pause_position'] = pos
    export['sim_pause_start'] = start
    export['sim_pause_end'] = end
    
    # Data result sets
    l = len(data.results)
    rawstart = np.zeros((l,),dtype=np.object)
    rawend = np.zeros((l,),dtype=np.object)
    fluxx = np.zeros((l,),dtype=np.object)
    fluxy = np.zeros((l,),dtype=np.object)
    densityx = np.zeros((l,),dtype=np.object)
    densityy = np.zeros((l,),dtype=np.object)
    densities = data.results.keys()
    for index in xrange(len(densities)):
        density = densities[index]
        start, end = dataRaw(data, density)
        rawstart[index] = list(start)
        rawend[index] = list(end)
        x,y = dataFlux(data,density)
        fluxx[index] = list(x)
        fluxy[index] = list(y)
        x,y = dataDensity((x,y), data.rate)
        densityx[index] = list(x)
        densityy[index] = list(y)
    export['sim_raw_start'] = rawstart
    export['sim_raw_end'] = rawend
    export['sim_flux_x'] = fluxx
    export['sim_flux_y'] = fluxy
    export['sim_density_x'] = densityx
    export['sim_density_y'] = densityy
    export['sim_densities'] = densities

    # Save to file
    f = open(filename, 'w')
    sio.savemat(f,export,do_compression=True)
    f.close()

def complete(filename):
    print "Accessing database..."
    results = Results(filename)
    print "Accessing positions..."
    positions = results.getPositions()
    print "Accessing densities..."
    densities = results.getDensities()
    print "Accessing experiment count..."
    experiments = results.getExperimentCount(densities[0])
    for beta in densities:
        for position in positions:
            print "Processing density %f position %d" % (beta, position)
            data = results.getData(beta, position)
            fx,fy = dataFlux(data, experiments)
            dx, dy = dataDensity((fx,fy), beta)
            export = {'fluxx': fx,
                      'fluxy': fy}
#                      'densityx': dx,
#                      'densityy': dy}
            f = open("results/d%fp%dflux.mat" % (beta, position), 'w')
            sio.savemat(f,export)
            f.close()
            
            f = open("results/d%fp%draw.mat" % (beta, position), 'w')
            export = {'raw': data}
            sio.savemat(f,export)
            f.close()
    
    
if __name__ == "__main__":
    try:
        rfile = sys.argv[1]
        print "Results file: " + rfile
    except IndexError:
        print "Bad parameters, should be 'analysis.py resultsfile'"
        quit()
    complete(rfile)
