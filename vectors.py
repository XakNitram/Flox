from dataclasses import dataclass
from math import tau, cos, sin, atan2, sqrt
from random import random


@dataclass
class Vec2:
    x: float = 0.
    y: float = 0.

    @classmethod
    def from_random(cls, strength: float):
        angle = tau * random()
        return cls(
            strength * cos(angle),
            strength * sin(angle)
        )

    @classmethod
    def from_scalar(cls, val: float):
        return Vec2(val, val)

    @classmethod
    def from_polar(cls, magnitude, angle):
        return Vec2(magnitude * cos(angle), magnitude * sin(angle))

    def with_angle(self, angle: float):
        return Vec2.from_polar(self.magnitude, angle)

    def with_magnitude(self, magnitude: float):
        try:
            return self.muls(magnitude / self.magnitude)
        except ZeroDivisionError:
            return self.from_polar(magnitude, 0.)

    def normalized(self) -> "Vec2":
        mag = self.magnitude
        return Vec2(self.x / mag, self.y / mag)

    def normalize(self):
        ratio = 1 / self.magnitude
        self.muls(ratio)

    def limited(self, magnitude: float):
        my_mag = self.distance_2(Vec2())
        if 0. < magnitude * magnitude < my_mag:
            ratio = magnitude / self.magnitude
            return Vec2(self.x * ratio, self.y * ratio)
        else:
            return Vec2(self.x, self.y)

    def limit(self, magnitude: float):
        my_mag = self.distance_2(Vec2())
        if 0. < magnitude * magnitude < my_mag:
            # if 0. < my_mag < magnitude * magnitude:
            ratio = magnitude / self.magnitude
            self.muls(ratio)

    def distance_to(self, other: "Vec2"):
        x = other.x - self.x
        y = other.y - self.y
        return sqrt(x * x + y * y)

    def distance_2(self, other: "Vec2"):
        x = other.x - self.x
        y = other.y - self.y
        return x * x + y * y

    def adds(self, val: float) -> "Vec2":
        self.x += val
        self.y += val
        return self

    def muls(self, val: float) -> "Vec2":
        self.x *= val
        self.y *= val
        return self

    def subs(self, val: float) -> "Vec2":
        self.x -= val
        self.y -= val
        return self

    def rsubs(self, val: float) -> "Vec2":
        self.x = val - self.x
        self.y = val - self.y
        return self

    def divs(self, val: float) -> "Vec2":
        self.x /= val
        self.y /= val
        return self

    def rdivs(self, val: float) -> "Vec2":
        self.x = val / self.x
        self.y = val / self.y
        return self

    def add(self, other: "Vec2") -> "Vec2":
        self.x += other.x
        self.y += other.y
        return self

    def sub(self, other: "Vec2") -> "Vec2":
        self.x -= other.x
        self.y -= other.y
        return self

    subtract = sub

    def mul(self, other: "Vec2") -> "Vec2":
        self.x *= other.x
        self.y *= other.y
        return self

    multiply = mul

    def div(self, other: "Vec2") -> "Vec2":
        self.x /= other.x
        self.y /= other.y
        return self

    divide = div

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: "Vec2") -> "Vec2":
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __isub__(self, other: "Vec2") -> "Vec2":
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x * other.x, self.y * other.y)

    def __imul__(self, other: "Vec2") -> "Vec2":
        self.x *= other.x
        self.y *= other.y
        return self

    def __truediv__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x / other.x, self.y / other.y)

    def __itruediv__(self, other: "Vec2") -> "Vec2":
        self.x /= other.x
        self.y /= other.y
        return self

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    @property
    def angle(self) -> float:
        return atan2(self.y, self.x)

    @property
    def magnitude(self) -> float:
        x, y = self.x, self.y
        return sqrt(x * x + y * y)

    @magnitude.setter
    def magnitude(self, val: float):
        try:
            ratio = val / self.magnitude
            self.muls(ratio)
        except ZeroDivisionError:
            pass

    def copy(self):
        return Vec2(self.x, self.y)
