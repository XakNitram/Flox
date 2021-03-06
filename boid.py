from ctypes import sizeof as size_in_memory
from math import cos, tau, sin
from random import random
from typing import List

from pyglet.gl import GLfloat

from drawables import BoidRenderer
from vectors import Vec2


class Boid:
    SIZE = 10.

    MAX_FORCE = 10.
    MAX_SPEED = 100.

    ALIGN_RANGE = 70.
    SEPARATE_RANGE = 25.

    __slots__ = "name", "position", "velocity", "acceleration"

    name: int
    position: Vec2
    velocity: Vec2
    acceleration: Vec2

    def __init__(self, name: int, x: float, y: float):
        self.name = name
        self.position = Vec2(x, y)
        self.velocity = Vec2.from_random(self.MAX_SPEED)
        self.acceleration = Vec2()

    @property
    def heading(self) -> float:
        return self.velocity.angle

    def alignment(self, neighbors: List["Boid"]) -> Vec2:
        steering = Vec2()
        if not len(neighbors):
            return steering

        total = 0

        for boid in neighbors:
            if boid is self:
                continue

            steering.add(boid.velocity)
            total += 1

        if total:
            steering.divs(total)
            steering.magnitude = self.MAX_SPEED
            steering.subtract(self.velocity)
            steering.limit(self.MAX_FORCE)

        return steering

    def cohesion(self, neighbors: List["Boid"]) -> Vec2:
        steering = Vec2()
        if not len(neighbors):
            return steering

        total = 0

        for boid in neighbors:
            if boid is self:
                continue

            steering.add(boid.position)
            total += 1

        if total:
            steering.divs(total)
            steering.sub(self.position)
            steering.magnitude = self.MAX_SPEED
            steering.subtract(self.velocity)
            steering.limit(self.MAX_FORCE)

        return steering

    def separation(self, neighbors: List["Boid"]) -> Vec2:
        steering = Vec2()
        if not len(neighbors):
            return steering

        total = 0
        # for boid, d in neighbors:
        for boid in neighbors:
            if boid is self:
                continue

            diff = self.position.copy()
            diff.subtract(boid.position)

            d2 = self.position.distance_2(boid.position)

            # Asking for forgiveness over permission.
            try:
                diff.divs(d2)
            except ZeroDivisionError:
                pass

            steering.add(diff)

            total += 1

        if total:
            steering.divs(total)
            steering.magnitude = self.MAX_SPEED
            steering.subtract(self.velocity)
            steering.limit(self.MAX_FORCE)

        return steering

    def seek(self, target: Vec2):
        steering = target.copy()
        steering.subtract(self.position)
        steering.magnitude = self.MAX_SPEED
        steering.subtract(self.velocity)
        steering.limit(self.MAX_FORCE)

        return steering


class Flock:
    def __init__(self, count: int, start: Vec2, bound_radius: float):
        self.bound = bound_radius
        self.count = count
        self.data: List[Boid] = [
            Boid(name, 100.0 * cos(angle) + start.x, 100.0 * sin(angle) + start.y)

            # pretty cool, these two will be evaluated as they're needed.
            for name, angle in zip(range(count), (random() * tau for _ in range(count)))
        ]
        self.distances = [([0.] * count) for _ in range(count)]
        self.renderer = BoidRenderer()

    def update(self, dt: float):
        boid_data = (GLfloat * (3 * self.count))()
        for i in range(self.count):
            boid = self.data[i]

            # TODO: Replace this distances array with a Quad-Tree data structure.
            for j in range(i + 1, self.count):
                other = self.data[j]

                distance = boid.position.distance_2(other.position)

                self.distances[i][j] = distance
                self.distances[j][i] = distance

            # ****** Update Boids ******
            boid.velocity += boid.acceleration
            # boid.velocity.magnitude = boid.MAX_SPEED
            boid.position += boid.velocity * Vec2(dt, dt)

            # reset acceleration
            boid.acceleration.muls(0.)

            # stay near the origin
            origin = Vec2(0., 0.)
            distance_to_origin = boid.position.distance_2(origin)
            bound = self.bound
            if distance_to_origin > bound * bound:
                origin_seek = boid.seek(origin)
                origin_seek.divs(1.5)
                boid.acceleration += origin_seek

            speed_up = boid.velocity.copy()
            speed_up.magnitude = boid.MAX_SPEED
            speed_up.subtract(boid.velocity)
            # speed_up.limit(boid.MAX_FORCE)
            speed_up.limit(boid.MAX_FORCE / 2)
            boid.acceleration.add(speed_up)

            # **** Alignment and Cohesion ****
            ar = boid.ALIGN_RANGE
            aclign_to = []
            for j, other in enumerate(self.data):
                if other is boid:
                    continue

                dist = self.distances[i][j]
                if dist < ar * ar:
                    aclign_to.append(other)

            alignment = boid.alignment(aclign_to)
            cohesion = boid.cohesion(aclign_to)

            # **** Separation ****
            # FIXME: This separation code is causing the boids to jitter. Why?
            sr = boid.SEPARATE_RANGE
            separate_from = []
            for j, other in enumerate(self.data):
                if other is boid:
                    continue

                dist = self.distances[i][j]
                if dist < sr * sr:
                    separate_from.append(other)
            separation = boid.separation(separate_from)

            # alignment.divs(8.)
            alignment.divs(4.)
            cohesion.divs(16.)
            separation.divs(2.)

            boid.acceleration.add(alignment)
            boid.acceleration.add(cohesion)
            boid.acceleration.add(separation)

            # ****** Update Drawable Shape ******
            index = i * 3
            boid_data[index + 0] = boid.position.x
            boid_data[index + 1] = boid.position.y
            boid_data[index + 2] = boid.heading

        self.renderer.update(boid_data, size_in_memory(boid_data))

    def draw(self):
        self.renderer.draw(self.count)
