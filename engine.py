from multiprocessing import Pool
from settings import Settings
from experiment import Experiment
from results import Results
import traceback, sys

def runexperiment(density, number, settings, resultsfile):
    exp = Experiment(settings, density)
    exp.run()
    Results(resultsfile).add(exp.results, density, number)
    print "done"
        
def doExperiments(settingsfile, resultsfile):
    """ Loads the given filename and runs experiments in parallel to meet the requirements within """
    # Generate variables
    settings = Settings(settingsfile)
    pool = Pool()

    # Queue all simulations
    for density in settings.densities:
        for number in xrange(settings.runs):
            print "Preparing to run experiment: density="+str(density)+" count="+str(number)
            pool.apply_async(runexperiment, [density, number, settings, resultsfile])
            
    # Wait for all simulations to terminate
    pool.close()
    pool.join()
    
def doExperimentsSingle(settingsfile, resultsfile):
    """ Same as doExperiments, but runs the experiments one at at time, for ease of debugging """
    # Generate variables
    settings = Settings(settingsfile)

    # Queue all  simulations
    for density in settings.densities:
        for number in xrange(settings.runs):
            print "Preparing to run experiment: density="+str(density)+" number="+str(number)
            runexperiment(density, number, settings, resultsfile)
    
if __name__ == "__main__":
    try:
        sfile = sys.argv[1]
        rfile = sys.argv[2]
        print "Settings file: " + sfile
        print "Results file: " + rfile
    except IndexError:
        print "Bad parameters, should be 'engine.py settingsfile resultsfile'"
        quit()
    if len(sys.argv) == 4 and sys.argv[3] == "--single":
        doExperimentsSingle(sfile, rfile)
    else:
        doExperiments(sfile, rfile)
    print "Experiments concluded :)"
        
