import ctypes as c
from dataclasses import dataclass
from math import sin, cos, pi
from typing import List

from pyglet.gl import *

from shader import Shader, World


@dataclass
class BoidModel:
    x: float
    y: float
    angle: float
    radius: float


Mat4 = (GLfloat * 16)


class BoidRenderer:
    # language=GLSL
    vertex = b"""
    #version 330 core
    layout(location = 0) in vec4 position;

    uniform mat4 u_Projection = mat4(1.0);
    uniform mat4 u_View = mat4(1.0);
    uniform mat4 u_Model = mat4(1.0);

    void main() {
        gl_Position = u_Projection * u_View * u_Model * position;
    }

    """

    # language=GLSL
    fragment = b"""
    #version 330 core

    layout(location = 0) out vec4 color;

    void main() {
        color = vec4(0.2, 0.4, 1.0, 1.0);
    }
    """

    _vao: GLuint
    _vbo: GLuint
    _ebo: GLuint
    _model: Mat4

    def __init__(self):
        self.data: List[BoidModel] = []
        self.shader = Shader(self.vertex, self.fragment)

        self.model_l = self.shader.get_uniform_location(b'u_Model')
        self._model = Mat4(
            1., 0., 0., 0.,
            0., 1., 0., 0.,
            0., 0., 1., 0.,
            0., 0., 0., 1.,
        )

        indices = (GLuint * 10)(0, 1, 1, 3, 3, 0, 1, 2, 2, 3)
        positions = (GLfloat * 8)(
            cos(5 * pi / 4), sin(5 * pi / 4),
            cos(0.),         sin(0.),
            cos(3 * pi / 4), sin(3 * pi / 4),
            0.5 * cos(pi),   0.5 * sin(pi)
        )

        self._vao = GLuint(0)
        self._vbo = GLuint(0)
        self._ebo = GLuint(0)

        glGenVertexArrays(1, c.byref(self._vao))
        glBindVertexArray(self._vao)

        glGenBuffers(1, c.byref(self._vbo))
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)

        glBufferData(
            GL_ARRAY_BUFFER, c.sizeof(positions),
            positions, GL_STATIC_DRAW
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

    def __getitem__(self, item: int):
        return self.data[item]

    def set_world(self, width: int, height: int):
        World(self.shader).set(width, height)

    def attach_model(self, x: float, y: float, angle: float, radius: float) -> int:
        name = len(self.data)
        self.data.append(BoidModel(x, y, angle, radius))
        return name

    def set_model_uniform(self, model: BoidModel):
        radius = model.radius
        ca = cos(model.angle)
        sa = sin(model.angle)
        self._model[:] = (
            radius * ca,  radius * sa, 0., 0.,
            radius * -sa, radius * ca, 0., 0.,
            0.,           0.,          1., 0.,
            model.x,      model.y,     0., 1.
        )

        self.shader.set_uniform_matrix4fv_raw(self.model_l, self._model)

    def draw(self):
        glBindVertexArray(self._vao)
        for model in self.data:
            self.set_model_uniform(model)
            with self.shader:
                glDrawElements(GL_LINES, 10, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
