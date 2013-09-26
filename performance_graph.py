import pylab
import sys
import csv
import dateutil
	

def parse(f):
	parsed = list(map(lambda delta: delta.second + delta.microsecond/1E6, 
						map(dateutil.parser.parse,
							zip(*list(csv.reader(f, delimiter='\t')))[1])))
	return list(sum(parsed[i:i+4]) for i in xrange(0,400,5))
		

with open("pauses_run_1/performance.csv", "rb") as f:
	# load data
	s1 = parse(f)
with open("pauses_run_2/performance.csv", "rb") as f:
	# load data
	s2 = parse(f)
with open("pauses_run_3/performance.csv", "rb") as f:
	# load data
	s3 = parse(f)
with open("pauses_run_4/performance.csv", "rb") as f:
	# load data
	s4 = parse(f)
with open("pauses_run_5/performance.csv", "rb") as f:
	# load data
	s5 = parse(f)
with open("pauses_run_6/performance.csv", "rb") as f:
	# load data
	s6 = parse(f)
	
	pylab.title("Performance at different densities")
	pylab.xlabel("Real time (sec)")
	pylab.ylabel("Simulation time (sec)")
	pylab.plot(xrange(0,400,5), s1, 'b-', xrange(0,400,5), s2, 'g-', xrange(0,400,5), s3, 'r-', xrange(0,400,5), s4, 'c-', xrange(0,400,5), s5, 'm-', xrange(0,400,5), s6, 'y-')
	
	pylab.legend(("0.1", "0.2", "0.3", "0.4", "0.5", "0.6"), loc='best')

	pylab.show()

