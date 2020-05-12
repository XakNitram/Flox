from ctypes import create_string_buffer, pointer, POINTER, cast, byref

from pyglet.gl import *

# language=GLSL
vertex_source = b'''
#version 330 core

layout(location = 0) in vec2 position;

uniform mat4 u_World = mat4(1.0);

void main() {
    gl_Position = u_World * vec4(position.x, position.y, 0.0, 1.0);
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


class ShaderProgram:
    id: GLuint

    def __init__(self, vertex: bytes, fragment: bytes):
        self.id = glCreateProgram()

        vs = self.compile_shader(GL_VERTEX_SHADER, vertex)
        fs = self.compile_shader(GL_FRAGMENT_SHADER, fragment)

        glAttachShader(self.id, vs)
        glAttachShader(self.id, fs)

        glLinkProgram(self.id)
        glValidateProgram(self.id)

        glDeleteShader(vs)
        glDeleteShader(fs)

    @staticmethod
    def compile_shader(mode: int, source: bytes) -> GLuint:
        # Python necessity. Create a char* array out of the source.
        buffer = create_string_buffer(source)
        c_shader = cast(
            pointer(pointer(buffer)),
            POINTER(POINTER(GLchar))
        )

        shader: GLuint = glCreateShader(mode)
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
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(result))
        if result.value == GL_FALSE:
            message_length = GLint()
            glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(message_length))
            error_buffer = create_string_buffer(message_length.value)

            glGetShaderInfoLog(
                shader,
                message_length,
                byref(message_length),
                cast(pointer(error_buffer), POINTER(GLchar))
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

    def set_world_matrix(self, width, height):
        """This can be abstracted but for now it works."""
        with self:
            name_buffer = create_string_buffer(b'u_World')
            location: int = glGetUniformLocation(
                self.id, cast(pointer(name_buffer), POINTER(GLchar)),
            )

            if location == -1:
                raise GLException(f"Failed to find uniform u_World.")
            else:
                data = (GLfloat * 16)(
                    +2 / width, +0.,       0., 0.,
                    +0.,        +2/height, 0., 0.,
                    +0.,        +0.,       1., 0.,
                    +0.,        +0.,       0., 1.
                )

                glUniformMatrix4fv(location, 1, GL_FALSE, data)

    def __enter__(self):
        glUseProgram(self.id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        glUseProgram(0)


_default_shader = ShaderProgram(vertex_source, fragment_source)


def get_default_shader():
    return _default_shader
