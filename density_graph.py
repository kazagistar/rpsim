import pylab
import sys
import csv

with open(sys.argv[1] + "/" + "densities.csv", "rb") as f:
	# load data
	data = list(map(float, densities) for densities in csv.reader(f, delimiter=','))
	# averages...
	pylab.title("Density over time")
	pylab.xlabel("Position")
	pylab.ylabel("Simulation time (sec)")
	pylab.imshow(data, vmin=0.0, vmax=0.5, aspect="auto")
	pylab.colorbar().set_label("Particle density")
	pylab.gca().invert_yaxis()
	if sys.argv[2]:
		pylab.savefig(sys.argv[2])
	else:
		pylab.show()
