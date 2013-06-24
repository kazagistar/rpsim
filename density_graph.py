import pylab
import sys
import csv

def list_form(matrix):
	for x, row in enumerate(matrix):
		for y, value in enumerate(row):
			yield x, y, value


with open(sys.argv[1] + "/" + "densities.csv", "rb") as f:
	# load data
	data = list(map(float, densities) for densities in csv.reader(f, delimiter='\t'))
	# averages...
	data = data[:100]
	pylab.title("Density over time with alpha 0.5")
	pylab.xlabel("Position")
	pylab.ylabel("Simulation time (sec)")
	pylab.imshow(data, vmin=0.0, vmax=0.5)
	pylab.colorbar().set_label("Particle density")
	pylab.gca().invert_yaxis()
	pylab.show()

