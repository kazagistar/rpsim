Instructions
============

1. Make sure you have  python

2. For graphing features, install matplotlib

3. Create a copy of example settings, and edit it as desired. "pydoc settings" should give you a comprehensive description of the options.

4. Run "python engine.py <your_settings_filename>" to run the simulation.

5. Results will appear in the folder specified, as comma separated values. flux.#.csv files are the flux for each run (the columns are the start time for each particle followed by each measurement location) and the densities.csv file is the averaged densities of all the runs, with each column being a position and each row being a single time step.

6. Additionally, there are a number of somewhat functional graphing tools (density_graph.py, performance_graph.py) which you can attempt to use at your discretion.


Features
========

TASEP simulations in the past have been implemented using kinetic monte carlo methods. The concept here is to list all the events that can occur, figure out their probabilities, and then pick one at random accordingly from the distribution. A common optimization is based on the following: because most of the events remaing the same after each event, the entire list does not have to be regenerated each time, but can instead be preserved with only some modifications made, usually via a balanced tree of some sort, which generally has a time complexity of O(log(N)), where N is the number of possible events.

For my colaboration, however, there was a critical additional requirement: a set of pauses had to be externally generated and passed through to the simulation. Pauses, also known as traffic lights, are when the a position's particle rate is set to 0 for some specified period of time. Data about these pauses had to have a fine moment-by-moment resultion, the results of this simulation could be compared to the alternative solution which used a partial differential equation. I had difficulty working out how I would fit this requirement into the monte carlo simulation, so instead I chose a widely different method and directly employed a discrete event simulator. This has a similar time complexity, and allows me to inject traffic lights as needed.

Another important points of the study was the ability to have different particle widths, which is fully supported. Also, it had to be adjustable as the models changed frequently, which is why python was chosen as the implementation language.


Implementation Details
======================

The program is a discrete event simulator. This means that fundimentally, it is built around an event priority queue. Each event is created with a time at which it will exectue, and added to this queue. The main loop of the program runs by pulling the event with the smallest time (the "next" event" from this queue and processing it, which might queue new events at future times. The priority queue is implemented as a heap, which has a time complexity of O(log(N)), where N is the number of events in the heap. Since the event processing is done in constant time, this is the fundimental defining time complexity of the simulation. Work is in progress to attempt an implementation using a calendar queue, to see if it is possible to exploit the known probability distributions of the simulation to approach O(1).

More specifically, there are two main types of events: particle creation, and particle movement. Some more details:

- Particle movement moves forward a particle and then calculates when the particle will be able to move next, and queues a new event. This is done by finding when the particle ahead of it (if there is one) will move, and then generating a random offset given the rate. For this to work, it is critical that each particle know ahead of time exactly when they will be able to move; thus, once the "next move time" is calculated, the data is stored so that it can be indexed directly by position from any particles that come up behind it, and so on. This means that an event only is called once per time it moves; an estimate of the number of events that will be processed in a given simulation is (Event count = number of positions * flux * time).

- Because a particle always has to move after the particle ahead of it, it is not neccessary to track the particle unless it is actually able to move forward. Thus, each time a particle movement occurs, it only queues up a new event if it has room in front; otherwise, it simply waits for the next move. At the same time, it checks behind to see if it was blocking something before it moved, and queues the precalculated particle movement event for the particle behind itself. This means that the number of events on the heap is capped by approximately P/2, where P is the maximum number of particles in the simulation.

- For each set of parameters, it is often desireable to run a simulation multiple times. These multiple simulations can all share a single discrete event simulator heap. This increases the number of events on the heap linearly per parallel simulation run, but the search times per event only increase as a logarithm, which could be a speed increase, though quantifying this experimentally is still future work.

- Pauses are generated once or passed in as settings, and then preprocessed by sorting them into a stack, so that each pause is only ever touched once during actual runtime. This is mentioned for completeness: a huge number of pauses can affect runtime, though only in very extreme cases. Each particle movement checks to see if it's generated "next move time" is a time that is paused, and if so, generates a new time starting from the end of the pause, until a valid time is found. 

- Particle width is done by indexed offsets in an array, and thus it is trivial to implement this feature in a fast way.

- Data is recorded in three ways: first, at regular simulation-time intervals, or "ticks", a repeating event is triggered. This event records to a file what fraction of the past time period a positon was full (which is data that is maintained through the course of other operations). Note: All of the density data in parallel simulations are averaged togeather as they are recorded to save space. This allows a good view of how the density of the simulations evolve over time. Second, also on ticks but in a separate file, are recorded some simple performance metrics. This can be easily extended to record other information as well if desired, and is useful for understanding performance in practice, though this is still rudamentary. Third, for each particle in each simulation, a number of recording locations are added, and the time at which each particle passes through them is recorded, which provides more detailed flux information. This data can be processed at any time after the simulation is complete.

