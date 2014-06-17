from math import tan, pi
from plugin import event
from event import KMCEvent

@event
def simulation_start(event, time, simulation):
    starter = Starter(simulation.settings)
    simulation.add_kmce(starter)

class Starter(KMCEvent):
    def __init__(self, settings):
        super().__init__(event="particle_created")
        self.rate = settings['alpha']
        self.settings = settings
        self.first_particle = None

    def event(self, time, simulation):
        """ Inserts a new particle into the doubly linked list of particles """
        new = Particle(settings=self.settings,
                       next=self.first_particle)
        try:
            self.first_particle.prev = new
            print("Creating second particle")
        except AttributeError:
        	pass
        self.first_particle = new
        new.starter = self
        simulation.add_kmce(new)


@event('particle_move')
def resume_starter(particle, time, simulation):
    # If the moving particle is moving past its fatness, it must be the first particle
    # This means the first part of the array is unblocked, and we can add another particle'
    if particle.fatness == particle.position:
        simulation.add_kmce(particle.starter)
        del particle.starter


twist_conversion_factor = 2 * pi / 10.5
torque_conversion_factor = 4.99

class Particle(KMCEvent):
    def __init__(self, settings, next=None, prev=None):
        super().__init__(event="particle_move")
        self.settings = settings
        self.click_offset_after = 0
        self.position = 0
        self.fatness = settings['fatness']
        self.next = next
        self.prev = prev
        self.update_rate()



    @property
    def length_after(self):
        return self.next.position - self.position - self.next.fatness

    @property
    def click_offset_before(self):
        return self.prev.click_offset_after
    @click_offset_before.setter
    def click_offset_before(self, value):
        self.prev.click_offset_before = value

    @property
    def length_before(self):
        return self.position - self.prev.position - self.fatness

    @property
    def torque(self):
        t = 0
        if self.next:
            t += self.click_offset_after
        if self.prev:
            t -= self.click_offset_before
        t *= twist_conversion_factor * torque_conversion_factor
        return t

    def update_rate(self):
        if not self.next or self.length_after > 0:
            x = self.torque
            rate = -0.0002 * pow(x,5) + 0.0008 * pow(x,4) + 0.0041 * pow(x,3) - 0.035 * pow(x,2) - 0.2166 * x + 22.3574
            self.rate = max(rate, 0)
        else:
            self.rate = 0

    def event(self, time, simulation):
        self.position += 1

        if self.position >= self.settings['size']:
            self.prev.next = None
            return

        try:
            self.click_offset_after -= 1
            self.next.update_rate()
        except AttributeError:
            pass
        try:
            self.click_offset_before += 1
            self.prev.update_rate()
        except AttributeError:
            pass

        self.update_rate()
        simulation.add_kmce(self)
