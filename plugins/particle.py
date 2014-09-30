from math import tan, pi, log
from plugin import event
from event import KMCEvent


@event
def simulation_start(simulation, **_):
    starter = Starter(simulation.settings)
    simulation.add_kmce(starter)


class Starter(KMCEvent):
    def __init__(self, settings):
        super(Starter, self).__init__()
        self.rate = settings['alpha']
        self.first_particle = None

    def event(self, time, simulation):
        """ Inserts a new particle into the doubly linked list of particles """
        if self.first_particle and self.first_particle.position >= simulation.settings['size']:
            self.first_particle = None
        new = Particle(settings=simulation.settings, next=self.first_particle)
        if self.first_particle:
            self.first_particle.prev = new
        self.first_particle = new
        new.starter = self
        simulation.add_kmce(new)
        simulation.plugins.trigger(event="particle_start", particle=new, time=time, simulation=simulation)


@event('particle_move')
def resume_starter(particle, simulation, **_):
    # If the moving particle is moving past its fatness, it must be the first particle
    # This means the first part of the array is unblocked, and we can add another particle'
    if particle.top_width == particle.position:
        simulation.add_kmce(particle.starter)
        particle.starter = None


# Rotation per base pair
twist_conversion_factor = 2 * pi / 10.5

torque_conversion_factor = (50 / 3.0) * pi / 2


class Particle(KMCEvent):
    def __init__(self, settings, next=None, prev=None):
        super(Particle, self).__init__()
        self.settings = settings
        self.position = 0
        self.top_width = settings['top_width']
        self.base_width = settings['base_width']
        self.next = next
        self.prev = prev
        if self.next:
            self.original_length_after = next.position - settings['base_width']
        else:
            self.original_length_after = 0
        self.update_rate()

    def torque(self):
        t = 0
        if self.next:
            la = self.next.position - self.position - self.base_width
            ola = self.original_length_after
            t += log(ola * 1.0 / la)
        if self.prev:
            lb = self.position - self.prev.position - self.base_width
            olb = self.prev.original_length_after
            t -= log(olb * 1.0 / lb)
        return twist_conversion_factor * torque_conversion_factor * 3 * t

    # The rate formula is monotonically decreasing
    def update_rate(self):
        if not self.next or (self.next.position - self.position - self.top_width > 0):
            x = self.torque()
            rate = -0.0002 * pow(x, 5) + 0.0008 * pow(x, 4) + 0.0041 * pow(x, 3) - 0.035 * pow(x, 2) - 0.2166 * x + 22.3574
            self.rate = max(rate, 0)
        else:
            self.rate = 0

    def event(self, time, simulation):
        self.position += 1
        if self.position >= self.settings['size']:
            simulation.plugins.trigger(event="particle_end", particle=self, time=time, simulation=simulation)
            if self.prev:
                self.prev.next = None
                self.prev.update_rate()
            return

        if self.next:
            self.next.update_rate()
        if self.prev:
            self.prev.update_rate()

        self.update_rate()
        simulation.add_kmce(self)
        simulation.plugins.trigger(event="particle_move", particle=self, time=time, simulation=simulation)
        
    def __str__(self):
        ola = self.original_length_after if self.next else "X"
        olb = self.prev.original_length_after if self.prev else "X"
        return "Particle(rate={0}, pos={1}, olb={3}, ola={2})".format(self.rate, self.position, ola, olb)
