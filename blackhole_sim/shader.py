from OpenGL.GL import *
import numpy as np

class Shader:
    def __init__(self, vert_path, frag_path):
        with open(vert_path, 'r') as f:
            v_code = f.read()
        with open(frag_path, 'r') as f:
            f_code = f.read()
            
        v_shader = self.compile_shader(v_code, GL_VERTEX_SHADER)
        f_shader = self.compile_shader(f_code, GL_FRAGMENT_SHADER)
        
        self.program = glCreateProgram()
        glAttachShader(self.program, v_shader)
        glAttachShader(self.program, f_shader)
        glLinkProgram(self.program)
        
        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            raise Exception(glGetProgramInfoLog(self.program).decode())
            
        glDeleteShader(v_shader)
        glDeleteShader(f_shader)

    def compile_shader(self, code, type):
        shader = glCreateShader(type)
        glShaderSource(shader, code)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            raise Exception(glGetShaderInfoLog(shader).decode())
        return shader

    def use(self):
        glUseProgram(self.program)

    def sm4(self, name, val):
        loc = glGetUniformLocation(self.program, name)
        glUniformMatrix4fv(loc, 1, GL_TRUE, val)

    def sf(self, name, val):
        loc = glGetUniformLocation(self.program, name)
        glUniform1f(loc, val)

    def si(self, name, val):
        loc = glGetUniformLocation(self.program, name)
        glUniform1i(loc, val)

    def sv2(self, name, x, y):
        loc = glGetUniformLocation(self.program, name)
        glUniform2f(loc, x, y)

    def sv3(self, name, x, y, z):
        loc = glGetUniformLocation(self.program, name)
        glUniform3f(loc, x, y, z)
        
    def sv4(self, name, x, y, z, w):
        loc = glGetUniformLocation(self.program, name)
        glUniform4f(loc, x, y, z, w)

    def sb(self, name, val):
        loc = glGetUniformLocation(self.program, name)
        glUniform1i(loc, 1 if val else 0)
