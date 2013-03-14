#!/usr/bin/python

def writeResults(results, filename):
    with open(filename, "w") as f:
        f.write("\n".join("\t".join((str(i) for i in line))))
