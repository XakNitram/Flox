import ctypes as c
from dataclasses import dataclass
from typing import Tuple, Dict, Iterator, ClassVar

from pyglet.gl import *


# language=GLSL
vertex_source = b'''
#version 330 core

layout(location = 0) in vec2 position;

uniform mat4 u_Projection = mat4(1.0);

void main() {
    gl_Position = u_Projection * vec4(position.x, position.y, 0.0, 1.0);
}
'''

# language=GLSL
fragment_source = b'''
#version 330 core

layout(location = 0) out vec4 color;

void main() {
    color = vec4(0.2, 0.4, 1.0, 1.0);
}
'''


@dataclass
class Location:
    value: int

    def __bool__(self):
        return self.value != -1

    def exists(self) -> bool:
        return bool(self)

    def __int__(self):
        return self.value


class Uniform:
    name: ClassVar[bytes]
    uniform: Location

    __slots__ = "program", "uniform"

    def __init__(self, program: "Shader"):
        self.program = program
        self.uniform = self.program.get_uniform_location(self.name)


class World(Uniform):
    name: bytes = b'u_Projection'

    def set(self, width: int, height: int):
        if self.uniform:
            self.program.set_uniform_matrix4fv(
                self.uniform, (
                    2 / width, 0.,         0., 0.,
                    0.,        2 / height, 0., 0.,
                    0.,        0.,         1., 0.,
                    0.,        0.,         0., 1.,
                )
            )


Mat4 = (GLfloat * 16)


# noinspection PyMethodMayBeStatic
class Shader:
    location_map: Dict[bytes, Location]
    id: GLuint

    def __init__(self, vertex: bytes, fragment: bytes):
        self.location_map = {}

        self.id = glCreateProgram()

        vs: GLuint = self.compile_shader(GL_VERTEX_SHADER, vertex)
        fs: GLuint = self.compile_shader(GL_FRAGMENT_SHADER, fragment)

        glAttachShader(self.id, vs)
        glAttachShader(self.id, fs)

        glLinkProgram(self.id)
        glValidateProgram(self.id)

        glDeleteShader(vs)
        glDeleteShader(fs)

    @staticmethod
    def compile_shader(mode: int, source: bytes):
        # Python necessity. Create a char* array out of the source.
        buffer = c.create_string_buffer(source)
        c_shader = c.cast(
            c.pointer(c.pointer(buffer)),
            c.POINTER(c.POINTER(GLchar))
        )

        shader: gl.GLuint = glCreateShader(mode)
        glShaderSource(
            shader,  # created shader (GLuint/u_long)
            1,  # number of shader sources attaching (GLsizei/int)
            c_shader,  # array of source strings (GLchar**/char**)
            None  # array of source string lengths or nullptr (GLint*/int*)
        )

        glCompileShader(shader)

        # TODO: Error handling
        result = GLint(2)
        # i - integer; v - vector
        glGetShaderiv(shader, GL_COMPILE_STATUS, c.byref(result))
        if result.value == GL_FALSE:
            message_length = GLint()
            glGetShaderiv(shader, GL_INFO_LOG_LENGTH, c.byref(message_length))
            error_buffer = c.create_string_buffer(message_length.value)

            glGetShaderInfoLog(
                shader,
                message_length,
                c.byref(message_length),
                c.cast(c.pointer(error_buffer), c.POINTER(GLchar))
                # error_buffer
            )

            if mode == GL_VERTEX_SHADER:
                shader_type = "vertex"
            elif mode == GL_FRAGMENT_SHADER:
                shader_type = "fragment"
            else:
                shader_type = "unknown"

            glDeleteShader(shader)

            raise Exception(f"Failed to compile {shader_type} shader: {str(error_buffer.value, 'ascii')}")
            # return gl.GLuint(0)

        return shader

    def get_uniform_location(self, name: bytes) -> Location:
        try:
            location = self.location_map[name]
        except KeyError:
            name_buffer = c.create_string_buffer(name)
            raw_location: int = glGetUniformLocation(
                self.id, c.cast(c.pointer(name_buffer), c.POINTER(GLchar))
            )

            self.location_map[name] = location = Location(raw_location)

        # assert uniform != -1, f"Unable to find uniform {name.decode('ascii')}"

        return location

    def set_uniform_1i(self, location: Location, value: int):
        with self:
            glUniform1i(location, value)

    def set_uniform_4f(self, location: Location, data: Iterator[float]):
        with self:
            glUniform4f(location, *data)

    def set_uniform_matrix4fv(self, location: Location, data: Tuple[float, ...]):
        with self:
            c_data = (GLfloat * len(data))(*data)
            glUniformMatrix4fv(location, 1, GL_FALSE, c_data)

    def set_uniform_matrix4fv_raw(self, location: Location, c_data: Mat4):
        with self:
            glUniformMatrix4fv(location, 1, GL_FALSE, c_data)

    def get_uniform_fv(self, location: Location, size: int) -> Tuple[float, ...]:
        with self:
            buffer = (GLfloat * size)()
            glGetUniformfv(self.id, location, buffer)

            return tuple(buffer)

    def get_uniform_iv(self, location: Location, size: int) -> Tuple[int, ...]:
        with self:
            buffer = (GLint * size)()
            glGetUniformiv(self.id, location, buffer)

            return tuple(buffer)

    def bind(self):
        glUseProgram(self.id)

    def unbind(self):
        glUseProgram(0)

    def __enter__(self) -> GLuint:
        self.bind()
        return self.id

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()


_default_shader = Shader(vertex_source, fragment_source)


def get_default_shader():
    return _default_shader
