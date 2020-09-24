import ctypes as c
from math import sin, cos, pi

from pyglet.gl import *

from shader import Shader, World


class BoidRenderer:
    # language=GLSL
    vertex = b"""
    #version 330 core
    layout(location = 0) in vec4 position;
    layout(location = 1) in vec2 offset;
    layout(location = 2) in float angle;

    uniform mat4 u_Projection = mat4(1.0);
    uniform float u_Scale = 10.0;

    void main() {
        float sa = u_Scale * sin(angle);
        float ca = u_Scale * cos(angle);
        mat4 model = mat4(
            ca,       sa,       0.0, 0.0,
            -sa,      ca,       0.0, 0.0,
            0.0,      0.0,      1.0, 0.0,
            offset.x, offset.y, 0.0, 1.0
        );
    
        gl_Position = u_Projection * model * position;
    }
    """

    # language=GLSL
    fragment = b"""
    #version 330 core

    layout(location = 0) out vec4 color;

    void main() {
        color = vec4(1.0, 0.4, 0.2, 1.0);
    }
    """

    scale = 10.0

    __slots__ = "shader", "_buffer_array", "_model_buffer", "_offset_buffer", "_index_buffer"

    _buffer_array: GLuint
    _model_buffer: GLuint
    _offset_buffer: GLuint
    _index_buffer: GLuint

    def __init__(self, max_boids=256):
        self.shader = Shader(self.vertex, self.fragment)

        indices = (GLuint * 10)(0, 1, 1, 3, 3, 0, 1, 2, 2, 3)
        positions = (GLfloat * 8)(
            cos(5 * pi / 4), sin(5 * pi / 4),
            cos(0.),         sin(0.),
            cos(3 * pi / 4), sin(3 * pi / 4),
            0.5 * cos(pi),   0.5 * sin(pi)
        )

        self._buffer_array = GLuint(0)
        self._model_buffer = GLuint(0)
        self._offset_buffer = GLuint(0)
        self._index_buffer = GLuint(0)

        glGenVertexArrays(1, c.byref(self._buffer_array))
        glBindVertexArray(self._buffer_array)

        glGenBuffers(1, c.byref(self._model_buffer))
        glBindBuffer(GL_ARRAY_BUFFER, self._model_buffer)

        glBufferData(
            GL_ARRAY_BUFFER, c.sizeof(positions),
            positions, GL_STATIC_DRAW
        )

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * c.sizeof(GLfloat), None)

        glGenBuffers(1, c.byref(self._offset_buffer))
        glBindBuffer(GL_ARRAY_BUFFER, self._offset_buffer)

        glBufferData(GL_ARRAY_BUFFER, (3 * c.sizeof(GLfloat)) * max_boids, None, GL_STREAM_DRAW)

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 3 * c.sizeof(GLfloat), None)
        glVertexAttribDivisor(1, 1)

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(
            2, 1, GL_FLOAT, GL_FALSE, 3 * c.sizeof(GLfloat),

            # weird offset thing
            c.c_void_p(2 * c.sizeof(GLfloat))
        )
        glVertexAttribDivisor(2, 1)

        glGenBuffers(1, c.byref(self._index_buffer))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._index_buffer)
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

    def set_world(self, width: int, height: int):
        World(self.shader).set(width, height)

    def update(self, data: c.Array, size: int):
        glBindVertexArray(self._buffer_array)
        glBindBuffer(GL_ARRAY_BUFFER, self._offset_buffer)

        glBufferSubData(GL_ARRAY_BUFFER, 0, size, data)

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, count: int):
        with self.shader:
            glBindVertexArray(self._buffer_array)
            glDrawElementsInstanced(GL_LINES, 10, GL_UNSIGNED_INT, None, count)
            glBindVertexArray(0)
