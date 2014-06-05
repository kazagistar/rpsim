import random
from os import path
from experiment import ExperimentSet
from math import log
from settings import load
from multiprocessing import Pool

def generate_pause_length():
	if random.random() < 0.6:
		return -1.2/log(random.random())
	else:
		return -6/log(random.random())

def generate_pauses(position_count, pause_count, simulation_length):
	pauses = []
	for number in range(pause_count):
		pauses.append((
			random.randrange(start=1, stop=position_count-1),
			random.random() * simulation_length,
			generate_pause_length()))
	pauses = [(position, start, start+length)
		      for position, start, length in pauses if length <= 40]
	return pauses
		
def write_pauses(pauses, folder):
	with open(path.join(folder, "pauses.csv"), "w") as pause_file:
		pause_file.write("\n".join("%i\t%f\t%f" % pause for pause in pauses))

def inject_pauses(settings, output_folder, count):
	pauses = generate_pauses(settings["size"], count, settings["time"])
	write_pauses(pauses, output_folder)
	settings["pauses"] = pauses

def spawn_simulation(infile, pauses, outfolder):
	settings = load(infile)
	write_pauses(pauses, outfolder)
	settings["pauses"] = pauses
	experiment = ExperimentSet(settings, outfolder)
	experiment.run()

if __name__ == "__main__":
	temp = load("pauses_run_1.json")
	pauses = generate_pauses(temp["size"], 120, temp["time"])
	
	pool = Pool(6)
	pool.apply_async(spawn_simulation,  ("pauses_run_1.json", pauses, "pauses_run_1"))
	pool.apply_async(spawn_simulation,  ("pauses_run_2.json", pauses, "pauses_run_2"))
	pool.apply_async(spawn_simulation,  ("pauses_run_3.json", pauses, "pauses_run_3"))
	pool.apply_async(spawn_simulation,  ("pauses_run_4.json", pauses, "pauses_run_4"))
	pool.apply_async(spawn_simulation,  ("pauses_run_5.json", pauses, "pauses_run_5"))
	pool.apply_async(spawn_simulation,  ("pauses_run_6.json", pauses, "pauses_run_6"))
	pool.close()
	pool.join()
