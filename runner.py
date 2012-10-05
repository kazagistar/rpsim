#!/usr/bin/python
class Runner(Event):
    """ The runner represents a RNA polymeraze molecule. Each time it moves, it generates a
    "next time" to move."""
    def __init__(self, time, pos):
        Event.__init__(self, time)
        self.pos = pos
        
    def run(self, experiment):
        # If at the end, store results and remove from list
        if self.pos + experiment.settings.fatness +1 >= len(experiment.positions):
            self.record.append(self.time)
            experiment.results.append(self.record)
            experiment.positions[self.pos].runner = None
            return
        # Record the time if we are at a recorder
        if experiment.positions[self.pos].recorder:
            self.record.append(self.time)
        # Move forward
        experiment.positions[self.pos].runner = None
        self.pos += 1
        experiment.positions[self.pos].runner = self
        # Get new time
        self.time = self.nextTime(experiment, self.time + nextRandomTime(experiment.settings.rate), experiment.positions[self.pos + experiment.settings.fatness].runner)
        # Requeue
        heappush(experiment.heap, self)
        
    def __str__(self):
        return "Runner(position=" + str(self.pos) + ", time=" + str(self.time) + ")"
    
    def nextTime(self, experiment, time, next):
        """ Generate a time to move next, given a current time."""
        settings = experiment.settings
        endpause = experiment.positions[self.pos].endOfPause(time)
        if endpause != time: # Current time is paused
            if settings.wait_pause == 1:
                time = endpause
                time += nextRandomTime(settings.rate)
            else:
                while time < endpause:
                    time += nextRandomTime(settings.rate)
            return self.nextTime(experiment, time, next)
        elif (next is not None) and (next.time > time): # Current time is blocked
            if settings.wait_block == 1:
                time = next.time
                time += nextRandomTime(settings.rate)
            else:
                while time < next.time:
                    time += nextRandomTime(settings.rate)
            return self.nextTime(experiment, time, next)
        else:
            return time
