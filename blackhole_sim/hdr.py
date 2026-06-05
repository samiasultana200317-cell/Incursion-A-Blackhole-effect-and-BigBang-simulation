from OpenGL.GL import *
import numpy as np
import ctypes

class HDR:
    def __init__(self, w, h):
        self.w, self.h = w, h
        
        # scene_fbo
        self.scene_fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.scene_fbo)
        
        # Attachments 0: Color, 1: Bright, 2: ID
        self.tex_scene = self.create_float_tex(w, h, GL_RGBA16F)
        self.tex_bright = self.create_float_tex(w, h, GL_RGBA16F)
        self.tex_id = self.create_float_tex(w, h, GL_RGBA32F)
        
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.tex_scene, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, self.tex_bright, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, self.tex_id, 0)
        
        # Depth/Stencil
        self.rbo_depth = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.rbo_depth)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, w, h)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.rbo_depth)
        
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Scene FBO incomplete")
            
        # lens_fbo
        self.lens_fbo = glGenFramebuffers(1)
        self.tex_lensed = self.create_float_tex(w, h, GL_RGBA16F)
        glBindFramebuffer(GL_FRAMEBUFFER, self.lens_fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.tex_lensed, 0)
        
        # ping_fbo for bloom
        self.ping_fbos = glGenFramebuffers(2)
        self.ping_texs = [self.create_float_tex(w, h, GL_RGBA16F) for _ in range(2)]
        for i in range(2):
            glBindFramebuffer(GL_FRAMEBUFFER, self.ping_fbos[i])
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.ping_texs[i], 0)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        # Quad
        self.quad_vao = self.create_quad()

    def cleanup(self):
        glDeleteFramebuffers(1, [self.scene_fbo])
        glDeleteTextures([self.tex_scene, self.tex_bright, self.tex_id])
        glDeleteRenderbuffers(1, [self.rbo_depth])
        glDeleteFramebuffers(1, [self.lens_fbo])
        glDeleteTextures([self.tex_lensed])
        glDeleteFramebuffers(2, self.ping_fbos)
        glDeleteTextures(self.ping_texs)

    def resize(self, w, h):
        self.cleanup()
        self.__init__(w, h)

    def create_float_tex(self, w, h, format):
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, format, w, h, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        return tex

    def create_quad(self):
        verts = np.array([
            -1, -1, 0, 0, 0,
             1, -1, 0, 1, 0,
             1,  1, 0, 1, 1,
            -1,  1, 0, 0, 1,
        ], dtype=np.float32)
        indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)
        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        ebo = glGenBuffers(1)
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 20, None)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, False, 20, ctypes.c_void_p(12))
        return vao

    def bind_scene(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.scene_fbo)
        glViewport(0, 0, self.w, self.h)
        glDrawBuffers(3, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2])

    def lensing_pass(self, shader, bh_screen, rs_screen, strength):
        glBindFramebuffer(GL_FRAMEBUFFER, self.lens_fbo)
        shader.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.tex_scene)
        shader.si("uScene", 0)
        shader.sv2("uBHScreen", bh_screen[0], bh_screen[1])
        shader.sf("uRsScreen", rs_screen)
        shader.sf("uStrength", strength)
        self.draw_quad()

    def bloom_pass(self, shader, iters=8):
        horizontal = True
        first_iteration = True
        shader.use()
        for i in range(iters):
            glBindFramebuffer(GL_FRAMEBUFFER, self.ping_fbos[int(horizontal)])
            shader.sb("horizontal", horizontal)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.tex_bright if first_iteration else self.ping_texs[int(not horizontal)])
            shader.si("image", 0)
            self.draw_quad()
            horizontal = not horizontal
            first_iteration = False
        return self.ping_texs[int(not horizontal)]

    def composite(self, shader, exposure, bloom_str, bloom_tex):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        shader.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.tex_lensed)
        shader.si("uScene", 0)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, bloom_tex)
        shader.si("uBloom", 1)
        shader.sf("uExposure", exposure)
        shader.sf("uBloomStr", bloom_str)
        self.draw_quad()

    def draw_quad(self):
        glBindVertexArray(self.quad_vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

    def read_id(self, x, y):
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.scene_fbo)
        glReadBuffer(GL_COLOR_ATTACHMENT2)
        pixel = glReadPixels(x, self.h - y, 1, 1, GL_RGBA, GL_FLOAT)
        return int(pixel[0][0][0] * 10 + 0.5)
