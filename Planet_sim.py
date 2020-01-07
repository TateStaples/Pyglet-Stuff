import pyglet
from math import *
from time import time

window = pyglet.window.Window()
window.width = 640
window.height = 640

# basic simulatoin of our solar system


@window.event
def on_key_press(symbol, mod):
    global slow_mo, unit_per_pixel
    if symbol == pyglet.window.key.UP:
        slow_mo /= 2
    elif symbol == pyglet.window.key.DOWN:
        slow_mo *= 2
    elif symbol == pyglet.window.key.LEFT:
        unit_per_pixel -= .00001
        set_conversion()
    elif symbol == pyglet.window.key.RIGHT:
        unit_per_pixel += .00001
        set_conversion()
    elif symbol == pyglet.window.key.SPACE:
        for planet in Planet.all_planets:
            planet.x_vel *= -1
            planet.y_vel *= -1
            planet.z_vel *= -1


def tick(dt):
    update(dt/slow_mo)
    draw()


def update(dt):
    for planet in Planet.all_planets:
        planet.apply_all(dt)
    # set_conversion()
    for planet in Planet.all_planets:
        planet.move(dt)


def draw():
    window.clear()
    for planet in Planet.all_planets:
        planet.draw()


def center(images):
    """Sets an image's anchor point to its center"""
    for image in images:
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2


def set_conversion():
    global current_conversion, unit_per_pixel, desired_width
    current_conversion = unit_per_pixel / desired_width


def mass_converter(x):
    return x / 2000000


class Planet(pyglet.sprite.Sprite):
    all_planets = []
    gravitation_constant = 4.302 * 10**-3  # 10000000000

    '''
    Units:
    distance: parsecs
    velocity: kilometers/second
    mass: solar_units
    time = years?
    '''

    def __init__(self, image, cords, mass, velocities=(0, 0, 0), image_dimensions=(50, 50)):
        self.x_vel, self.y_vel, self.z_vel = velocities
        self.mass = mass
        self.real_x, self.real_y, self.real_z = cords
        x, y = self.get_screen_pos()
        super(Planet, self).__init__(image, x=x, y=y)
        w, h = image_dimensions
        self.scale_x = w/self.width
        self.scale_y = h/self.height
        self.all_planets.append(self)

    def apply_all(self, dt):
        for planet in self.all_planets:
            if planet is self:
                continue
            self.apply_planet(planet, dt)

    def apply_planet(self, other_planet, dt):
        x_force, y_force, z_force = self.get_force(other_planet)
        self.apply_force(x_force, y_force, z_force, dt)

    def apply_force(self, x, y, z, dt):
        self.x_vel += x/self.mass * dt
        self.y_vel += y/self.mass * dt
        self.z_vel += z/self.mass * dt
        # print(f"Force: x={x}, y={y}, z={z}")

    def get_force(self, other_planet):
        delta_x = self.real_x - other_planet.real_x
        delta_y = self.real_y - other_planet.real_y
        delta_z = self.real_z - other_planet.real_z
        dis = self.pathag([delta_x, delta_y, delta_z])
        mass1 = self.mass
        mass2 = other_planet.mass
        magnitude = (self.gravitation_constant * mass1 * mass2) / (dis ** 2)
        r_hat = delta_x/dis, delta_y/dis, delta_z/dis
        components = (-hat*magnitude for hat in r_hat)
        return components

    def get_angle(self, other_planet):
        delta_x = self.real_x - other_planet.real_x
        delta_y = self.real_y - other_planet.real_y
        delta_z = self.real_z = other_planet.real_z
        if delta_y == 0:
            xy_angle = pi/2 if delta_x > 0 else 3*pi/2
        else:
            xy_angle = atan(delta_x/delta_y)
            if delta_y > 0:
                xy_angle += pi
        if delta_z == 0:
            xz_angle = pi/2 if delta_x > 0 else 3*pi/2
        else:
            xz_angle = atan(delta_x/delta_z)
            if delta_z > 0:
                xz_angle += pi
        return xy_angle, xz_angle  # note this is in radian

    def get_screen_pos(self):
        # todo change view angle
        try:
            x1, y1 = self.real_x-Sun.real_x, self.real_y - Sun.real_y  # keeps the screen centered on the Sun
        except NameError:
            x1, y1 = self.real_x, self.real_y
        x2, y2 = x1/current_conversion, y1/current_conversion
        # print(f"original x: {self.real_x}, streched: {x1}")
        return x2 + window.width/2, y2 + window.height/2

    def move(self, dt):
        if self is Earth and self.real_y < 0 and self.real_y + self.y_vel*dt > 0:
            global years_passed, start_time
            years_passed += 1
            print(f"{years_passed} years have passed, {time()-start_time}")
            start_time = time()
        self.real_x += self.x_vel * dt
        self.real_y += self.y_vel * dt
        self.real_z += self.z_vel * dt
        self.x, self.y = self.get_screen_pos()

    @staticmethod
    def pathag(vals):
        sum = 0
        for i in vals:
            sum += i**2
        return sqrt(sum)


if __name__ == '__main__':
    start_time = time()
    pyglet.resource.path = ["/Users/22staples/PycharmProjects/Pyglet_stuff/Images"]
    pyglet.resource.reindex()
    image = pyglet.resource.image
    sun = image("sun.png")
    earth = image("earth.png")
    mars = image("firey_planet.png")
    venus = image("orange_planet.png")
    mercury = image("gray_planet.png")
    jupiter = image("jupiter.png")
    saturn = image("pink_saturn.png")
    blue = image("blue_planet.png")

    center([sun, earth, venus, mars, mercury, jupiter, saturn, blue])
    unit_per_pixel = 0.0001456762698498
    desired_width = 300
    seconds_per_year = 10
    slow_mo = 952380.95 * seconds_per_year
    years_passed = 0
    current_conversion = unit_per_pixel / desired_width
    Sun = Planet(
        image=sun,
        image_dimensions=(20, 20),
        cords=(0, 0, 0),
        velocities=(0, 0, 0),
        mass=1  # in solar mass
    )
    Mercury = Planet(
        image=mercury,
        image_dimensions=(5, 5),
        cords=(0.000001876411208717, 0, 0),
        velocities=(0, 47.3625, 0),
        mass=mass_converter(0.330)  # in solar mass
    )
    Venus = Planet(
        image=venus,
        image_dimensions=(5, 5),
        cords=(-0.000003506523191419, 0, 0),
        velocities=(0, -35.0, 0),
        mass=mass_converter(4.87)  # in solar mass
    )
    Earth = Planet(
        image=earth,
        image_dimensions=(5, 5),
        cords=(0.000004848205817341, 0, 0),
        velocities=(0, 29.8, 0),
        mass=mass_converter(5.97)  # in solar mass
    )
    Mars = Planet(
        image=mars,
        image_dimensions=(5, 5),
        cords=(0, -0.00000738573600115, 0),
        velocities=(24.1, 0, 0),
        mass=mass_converter(0.642)  # in solar mass
    )
    Jupiter = Planet(
        image=jupiter,
        image_dimensions=(5, 5),
        cords=(0, -0.00002523270754934, 0),
        velocities=(13.1, 0, 0),
        mass=mass_converter(1898)  # in solar mass
    )
    Saturn = Planet(
        image=saturn,
        image_dimensions=(5, 5),
        cords=(0, -0.00004645657111737, 0),
        velocities=(9.7, 0, 0),
        mass=mass_converter(568)  # in solar mass
    )
    Uranus = Planet(
        image=blue,
        image_dimensions=(5, 5),
        cords=(0, -0.00009309138509567, 0),
        velocities=(6.8, 0, 0),
        mass=mass_converter(86.8)  # in solar mass
    )
    Neptune = Planet(
        image=blue,
        image_dimensions=(5, 5),
        cords=(0, -0.0001456762698498, 0),
        velocities=(5.4, 0, 0),
        mass=mass_converter(102)  # in solar mass
    )
    pyglet.clock.schedule_interval(tick, 1 / 120.0)
    pyglet.app.run()
