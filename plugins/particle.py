from math import tan, pi, log
from plugin import event
from event import KMCEvent


@event
def simulation_start(simulation, **_):
    starter = Starter(simulation.settings)
    simulation.add_kmce(starter)


class Starter(KMCEvent):
    def __init__(self, settings):
        super().__init__()
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
    if particle.fatness == particle.position:
        simulation.add_kmce(particle.starter)
        particle.starter = None


# Rotation per base pair
twist_conversion_factor = 2 * pi / 10.5

torque_conversion_factor = (50 / 3.0) * pi / 2


class Particle(KMCEvent):
    def __init__(self, settings, next=None, prev=None):
        super().__init__()
        self.settings = settings
        self.delta_distance_after = 0
        self.position = 0
        self.fatness = settings['fatness']
        self.next = next
        self.prev = prev
        self.update_rate()

    # Space between this particle and the back of the next one
    @property
    def length_after(self):
        return self.next.position - self.position - self.next.fatness

    # Space between the back of this particle and the previous one
    @property
    def length_before(self):
        return self.position - self.prev.position - self.fatness

    @property
    def delta_distance_before(self):
        return self.prev.delta_distance_after

    @delta_distance_before.setter
    def delta_distance_before(self, value):
        self.prev.delta_distance_after = value

    # HORRIBLE HACKS AND WRONG
    def torque(self):
        t = 0
        if self.next:
            la = self.length_after + 1
            ola = la - self.delta_distance_after
            t += log(ola / la)
        if self.prev:
            if self.length_before < 0:
                pass
            lb = self.length_before + 1
            olb = lb - self.delta_distance_before
            t -= log(olb / lb)
        return twist_conversion_factor * torque_conversion_factor * 3 * t

    # The rate formula is monotonically decreasing
    def update_rate(self):
        if not self.next or self.length_after > 0:
            x = self.torque()
            rate = -0.0002 * pow(x, 5) + 0.0008 * pow(x, 4) + 0.0041 * pow(x, 3) - 0.035 * pow(x,
                                                                                               2) - 0.2166 * x + 22.3574
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
            self.delta_distance_after -= 1
            self.next.update_rate()
        if self.prev:
            self.delta_distance_before += 1
            self.prev.update_rate()

        self.update_rate()
        simulation.add_kmce(self)
        simulation.plugins.trigger(event="particle_move", particle=self, time=time, simulation=simulation)

    def __str__(self):
        s = "Particle(rate={0}, pos={1}".format(self.rate, self.position)
        if self.prev:
            s += ", db={0}".format(self.delta_distance_before)
        if self.next:
            s += ", da={0}".format(self.delta_distance_after)
        return s + ")"