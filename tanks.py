# december 20, 2019

import pyglet
from math import *
import random
from time import time

window = pyglet.window.Window()


@window.event
def on_key_press(symbol, mod):
    if symbol == pyglet.window.key.UP:
        keyboard.up = True
    elif symbol == pyglet.window.key.DOWN:
        keyboard.down = True
    elif symbol == pyglet.window.key.RIGHT:
        keyboard.right = True
    elif symbol == pyglet.window.key.LEFT:
        keyboard.left = True
    elif symbol == pyglet.window.key.SPACE:
        for tank in Tank.tanks:
            delta_x, delta_y = forward(tank.sprite.height + 2, tank.sprite.rotation)
            bullet = Bullet(tank.sprite.rotation, tank.sprite.x+delta_x, tank.sprite.y+delta_y)


@window.event
def on_key_release(symbol, mod):
    if symbol == pyglet.window.key.UP:
        keyboard.up = False
    elif symbol == pyglet.window.key.DOWN:
        keyboard.down = False
    elif symbol == pyglet.window.key.RIGHT:
        keyboard.right = False
    elif symbol == pyglet.window.key.LEFT:
        keyboard.left = False


def tick(dt):
    # print(tank.sprite.rotation)
    user_input(dt)
    update(dt)
    draw()


def update(dt):
    for bullet in reversed(Bullet.bullets):
        bullet.move(dt)
        for tank in Tank.tanks:
            if bullet.hit_tank(tank):
                tank.been_hit()
                continue
        bullet.check_time()
    for ani in Animation.animations:
        ani.check_time()


def user_input(dt):
    # '''
    for tank in Tank.tanks:
        x, y = forward(Tank.speed * dt, tank.sprite.rotation)
        f, b, l, r = tank.get_valid_directions(dt)
        if keyboard.up and f:  # forward
            tank.sprite.y += y
            tank.sprite.x += x
        if keyboard.down and b:  # backward
            tank.sprite.y -= y
            tank.sprite.x -= x
        if keyboard.right and r:  # turn right
            tank.sprite.rotation += 120 * dt
        if keyboard.left and l:  # turn left
            tank.sprite.rotation -= 120 * dt
    '''
    x, y = forward(Tank.speed * dt, tank.sprite.rotation)
    if keyboard.up:  # forward
        for current_x, current_y in tank.get_hitbox():
            for wall in Wall.walls:
                if wall.did_collide((current_x, current_y), x, y):
                    break
        else:
            tank.sprite.y += y
            tank.sprite.x += x
    if keyboard.down:  # backward
        for current_x, current_y in tank.get_hitbox():
            for wall in Wall.walls:
                if wall.did_collide((current_x, current_y), -x, -y):
                    break
        else:
            tank.sprite.y -= y
            tank.sprite.x -= x

    # The formula for the chord length is: 2rsin(theta/2)
    radius = distance((tank.sprite.x + tank.sprite.width, tank.sprite.y + tank.sprite.height), tank.sprite.position)
    turn_amount = 120 * dt
    chord_length = 2 * radius * sin(radians(turn_amount)/2)
    if keyboard.right:  # turn right
        x, y = forward(chord_length, tank.sprite.rotation - turn_amount)
        for current_x, current_y in tank.get_hitbox():
            for wall in Wall.walls:
                if wall.did_collide((current_x, current_y), -x, -y):
                    break
        else:
            tank.sprite.rotation += turn_amount
    if keyboard.left:  # turn left
        x, y = forward(chord_length, tank.sprite.rotation + turn_amount)
        for current_x, current_y in tank.get_hitbox():
            for wall in Wall.walls:
                if wall.did_collide((current_x, current_y), -x, -y):
                    break
        else:
            tank.sprite.rotation -= turn_amount
    # '''


def forward(dis, rotation):
    radian = radians(rotation)
    x = sin(radian) * dis
    y = cos(radian) * dis
    return x, y


def draw():
    window.clear()
    for tank in Tank.tanks:
        tank.sprite.draw()
        for corner in tank.get_hitbox():
            pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
                                 ('v2i', corner)
                                 )
    for bullet in Bullet.bullets:
        bullet.sprite.draw()
    Wall.wall_batch.draw()
    for ani in Animation.animations:
        ani.thing.draw()


def center(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


def scale(image, scale):
    image.scale_x = scale
    image.scale_y = scale
    return image


def generate_random_wall():
    w = window.width
    h = window.height
    point1 = random.randint(0, w), random.randint(0, h)
    point2 = random.randint(0, w), random.randint(0, h)
    wall1 = Wall(point1, point2, "top")
    wall2 = Wall(point1, point2, "bottom")


def distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return sqrt((x1 - x2) **2 + (y1 - y2)**2)


def get_corners(sprite):
    x, y = sprite.position
    w, h = sprite.width/2, sprite.height/2
    heading = radians(sprite.rotation)
    angle_to_diagonal = atan(w / h)
    diagonal_dis = w / sin(angle_to_diagonal)
    angle_to_TR = heading + angle_to_diagonal
    angle_to_TL = heading - angle_to_diagonal
    angle_to_BR = heading - angle_to_diagonal + pi
    angle_to_BL = heading + angle_to_diagonal + pi
    x1, y1 = forward(diagonal_dis, degrees(angle_to_TL))
    x2, y2 = forward(diagonal_dis, degrees(angle_to_TR))
    x3, y3 = forward(diagonal_dis, degrees(angle_to_BL))
    x4, y4 = forward(diagonal_dis, degrees(angle_to_BR))
    # print(f"x change: {x1}, y change: {y1}, width: {w}, height: {h}")
    return [(int(x + x1), int(y + y1)),
            (int(x + x2), int(y + y2)),
            (int(x + x3), int(y + y3)),
            (int(x + x4), int(y + y4))]


pyglet.resource.path = ["/Users/22staples/PycharmProjects/Pyglet_stuff/Images"]
pyglet.resource.reindex()
image = pyglet.resource.image
bullet_pic = image("bullet.png")
tank_pic = image("tank.png")
explosion_pic = image("explosion.png")
center(bullet_pic)
center(tank_pic)
center(explosion_pic)


class Keyboard:
    left = False
    right = False
    up = False
    down = False
    w = False
    a = False
    s = False
    d = False
    space = False


class Bullet:
    pic = bullet_pic
    speed = 200
    scale = .03
    life_span = 5
    bullets = []

    def __init__(self, rotation, x, y):
        self.bullets.append(self)
        self.sprite = pyglet.sprite.Sprite(x=x, y=y, img=self.pic)
        self.sprite.rotation = rotation
        self.end_time = time() + self.life_span
        scale(self.sprite, self.scale)
        radian = radians(rotation)
        self.x_vel = cos(radian) * self.speed
        self.y_vel = sin(radian) * self.speed
        self.just_bounced = False

    def move(self, dt):
        jb = self.just_bounced
        self.just_bounced = False
        delta_x, delta_y = forward(self.speed * dt, self.sprite.rotation)
        if not jb:
            for wall in Wall.walls:
                if wall.did_collide((self.sprite.x, self.sprite.y), delta_x, delta_y):
                    self.sprite.rotation = wall.resulting_rotation(self.sprite.rotation)
                    delta_x, delta_y = forward(self.speed * dt, self.sprite.rotation)
                    # self.just_bounced = True
                    break
        self.sprite.x += delta_x
        self.sprite.y += delta_y

    def hit_tank(self, tank):
        dis = distance(tank.sprite.position, self.sprite.position)
        hit = dis < tank.sprite.height
        if hit:
            self.remove()
        return hit

    def check_time(self):
        if time() >= self.end_time:
            self.bullets.remove(self)
            del self

    def remove(self):
        self.bullets.remove(self)
        del self


class Tank:
    pic = tank_pic
    speed = 140
    scale = .15
    tanks = []

    def __init__(self, x, y):
        self.sprite = pyglet.sprite.Sprite(x=x, y=y, img=self.pic)
        self.sprite.rotation = random.randint(0, 360)
        scale(self.sprite, self.scale)
        self.tanks.append(self)

    def been_hit(self):
        boom = Animation(img=explosion_pic, scaler=0.15, cords=(self.sprite.x, self.sprite.x), timer=5)
        self.tanks.remove(self)
        del self

    def get_hitbox(self):
        me = self.sprite
        x, y = me.x, me.y
        return get_corners(self.sprite)
        return [(int(x), int(y))]

    def get_valid_directions(self, dt):
        x, y = forward(Tank.speed * dt, self.sprite.rotation)

        can_forward = True
        can_backward = True
        can_left = True
        can_right = True

        # The formula for the chord length is: 2rsin(theta/2)
        radius = distance((self.sprite.x + self.sprite.width, self.sprite.y + self.sprite.height),
                          self.sprite.position)
        turn_amount = 120 * dt
        chord_length = 2 * radius * sin(radians(turn_amount) / 2)
        x_right, y_right = forward(chord_length, self.sprite.rotation - turn_amount)
        x_left, y_left = forward(chord_length, self.sprite.rotation + turn_amount)

        for current_x, current_y in self.get_hitbox():
            for wall in Wall.walls:
                if can_forward and wall.did_collide((current_x, current_y), x, y):
                    can_forward = False
                elif can_backward and wall.did_collide((current_x, current_y), -x, -y):
                    can_backward = False

            for wall in Wall.walls:
                if can_right and wall.did_collide((current_x, current_y), x_right, y_right):
                    can_right = False
                if can_left and wall.did_collide((current_x, current_y), x_left, y_left):
                    can_left = False
        return can_forward, can_backward, can_left, can_right


class Wall:
    collision_dis = .1
    walls = []
    wall_batch = pyglet.graphics.Batch()

    def __init__(self, point1, point2, collision_direction):
        self.top_hit = collision_direction == "top"
        self.point1 = point1
        self.point2 = point2
        self.walls.append(self)
        x1, y1 = point1
        x2, y2 = point2
        self.wall_batch.add(2, pyglet.graphics.GL_LINES, None,
                            ('v2f', (x1, y1, x2, y2)))
        if x1 - x2 == 0:
            self.rise = abs(y1 - y2)
            self.run = 0
            self.slope = "undefined"
        elif x1 < x2:
            self.rise = y1 - y2
            self.run = x1 - x2
            self.slope = self.rise/self.run
        else:
            self.rise = y2 - y1
            self.run = x2 - x1
            self.slope = self.rise / self.run

    def my_line(self, x):
        x1, y1 = self.point1
        # y - y1 = m(x - x1)
        y = self.slope * (x - x1) + y1
        return y

    def did_collide(self, cords, delta_x, delta_y):
        x1, y1 = self.point1
        x2, y2 = self.point2
        x, y = cords
        new_x, new_y = x + delta_x, y + delta_y
        if x1 == x2 and self.between(y, y1, y2):  # handles verticle lines
            before_is_greater = x > x1
            after_is_greater = new_x >= x1
            return before_is_greater != after_is_greater
        if self.between(x, x1, x2):
            before_predicted_y = self.my_line(x)
            after_predicted_y = self.my_line(new_x)
            if self.top_hit:  # top
                if y < before_predicted_y:
                    return False
                return new_y < after_predicted_y
            else:  # bottom
                if y > before_predicted_y:
                    return False
                return new_y > after_predicted_y
        return False

    @staticmethod
    def between(focus, num1, num2):
        if num1 < num2:
            return num1 < focus < num2
        return num2 < focus < num1

    def resulting_rotation(self, income_rotation):
        income_rotation %= 360
        if income_rotation < 0:
            income_rotation += 360
        x1, y1 = self.point1
        x2, y2 = self.point2
        if y1 == y2:
            wall_angle = 90
        else:
            wall_angle = degrees(atan(self.run/self.rise))
            if self.rise < 0 and False:
                wall_angle += 90
        # print(f"slope: {self.slope}, angle: {wall_angle}")
        '''
        perpendicular_angle = wall_angle - 90 if moving_left else wall_angle - 90
        printing = False
        angle_of_incidence = income_rotation - perpendicular_angle if moving_left else income_rotation - perpendicular_angle
        output_angle = perpendicular_angle - angle_of_incidence if moving_left else perpendicular_angle - angle_of_incidence
        output_angle = output_angle + 180 if output_angle < 0 else output_angle
        if printing:
            print()
            print()
            print("incoming:", income_rotation)
            print("wall angle:", wall_angle)
            print("perpendicular angle:", perpendicular_angle)
            print("angle of incidence:", angle_of_incidence)
            print("result:", output_angle)
        return output_angle
        '''
        return 2*wall_angle - income_rotation


class Animation:
    animations = []

    def __init__(self, timer, cords, img, scaler):
        x, y = cords
        self.thing = pyglet.sprite.Sprite(img=img, x=x, y=y)
        scale(self.thing, scaler)
        self.animations.append(self)
        self.end_time = time() + timer

    def check_time(self):
        done = time() >= self.end_time
        if done:
            self.remove()

    def remove(self):
        self.animations.remove(self)
        del self


if __name__ == '__main__':
    keyboard = Keyboard()
    tank1 = Tank(200, 400)
    tank2 = Tank(400, 200)
    buffer = 5
    left_wall = Wall((buffer, buffer), (buffer, window.height - buffer), "top")
    right_wall = Wall((window.width - buffer, buffer), (window.width - buffer, window.height - buffer), "bottom")
    bottom_wall = Wall((buffer, buffer), (window.width - buffer, buffer), "top")
    top_wall = Wall((buffer, window.height - buffer), (window.width - buffer, window.height - buffer), "bottom")
    generate_random_wall()
    generate_random_wall()
    generate_random_wall()
    generate_random_wall()
    pyglet.clock.schedule_interval(tick, 1 / 120.0)
    pyglet.app.run()
