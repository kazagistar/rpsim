from settings import load
import sys
import csv
from math import ceil

try:
    output = sys.argv[2]
    import matplotlib
    matplotlib.use("Agg")
except:
    output = None
import pylab

settings = load(sys.argv[1])

with open(settings["output"] + "/" + "densities.csv", "rb") as f:
    # load data
    data = list(map(float, densities) for densities in csv.reader(f, delimiter=','))

    # fill in width
    dataFilled = []
    for tick in data:
        newTick = []
        length = len(tick)
        for pos in range(length):
            newTick.append(sum(tick[pos: min(pos + settings['fatness'], length)]))
        dataFilled.append(newTick)
    data = dataFilled

    # rescale data
    data = [row[::int(ceil(len(row) / 1000.0))] for row in data][::int(ceil(len(data) / 1000.0))]
        
    # display
    pylab.title("Density over time")
    pylab.xlabel("Position")
    pylab.ylabel("Simulation time (sec)")
    extents = [0, settings['size'], settings['time'], 0]
    pylab.imshow(data, vmin=0.0, vmax=1, aspect="auto", extent=extents)
    pylab.colorbar().set_label("Particle density")
    pylab.gca().invert_yaxis()
    if output:
        pylab.savefig(output)
    else:
        pylab.show()
