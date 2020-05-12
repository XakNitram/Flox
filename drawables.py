import ctypes as c
from math import sin, cos, pi

from pyglet.gl import *


class WireframeTriangle:
    __slots__ = 'positions', '_vao', '_vbo', '_ebo', 'x', 'y', 'angle', 'radius'

    _vao: GLuint
    _vbo: GLuint
    _ebo: GLuint

    def __init__(
            self, x: float, y: float, angle: float, radius: float
    ):
        self.x = x
        self.y = y
        self.angle = angle
        self.radius = radius

        indices = (GLuint * 10)(0, 1, 1, 3, 3, 0, 1, 2, 2, 3)
        self.positions = (GLfloat * 8)()
        self._set_positions(x, y, angle, radius)

        self._vao = GLuint(0)
        self._vbo = GLuint(0)
        self._ebo = GLuint(0)

        glGenVertexArrays(1, c.byref(self._vao))
        glBindVertexArray(self._vao)

        glGenBuffers(1, c.byref(self._vbo))
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)

        glBufferData(
            GL_ARRAY_BUFFER, c.sizeof(self.positions),
            self.positions, GL_STATIC_DRAW
        )

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * c.sizeof(GLfloat), None)
        glEnableVertexAttribArray(0)

        glGenBuffers(1, c.byref(self._ebo))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER, c.sizeof(indices),
            indices, GL_STATIC_DRAW
        )

        # We have to unbind the vertex array first.
        # Otherwise the other buffers will be disassociated
        # with the VAO when they're unbound.
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def _set_positions(
            self, x: float, y: float, angle: float, radius: float
    ):

        a1 = (5 * pi / 4)
        a2 = 0.
        a3 = (3 * pi / 4)
        a4 = pi

        rca = radius * cos(angle)
        rsa = radius * sin(angle)
        # This is what we have to deal with without numpy.
        self.positions[:] = (
            cos(a1) * rca + sin(a1) * -rsa + x,
            cos(a1) * rsa + sin(a1) * +rca + y,

            cos(a2) * rca + sin(a2) * -rsa + x,
            cos(a2) * rsa + sin(a2) * +rca + y,

            cos(a3) * rca + sin(a3) * -rsa + x,
            cos(a3) * rsa + sin(a3) * +rca + y,

            0.5 * cos(a4) * rca + 0.5 * sin(a4) * -rsa + x,
            0.5 * cos(a4) * rsa + 0.5 * sin(a4) * +rca + y,
        )

    def update(self):
        self._set_positions(self.x, self.y, self.angle, self.radius)

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, c.sizeof(self.positions), self.positions)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self):
        glBindVertexArray(self._vao)
        glDrawElements(GL_LINES, 10, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
