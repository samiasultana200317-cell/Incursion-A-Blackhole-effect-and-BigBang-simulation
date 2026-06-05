import numpy as np
from OpenGL.GL import *
import ctypes

class AccretionDisk:
    def __init__(self, rs):
        self.N = 30000
        self.rs = rs
        
        # All float32
        self.positions = np.zeros((self.N, 3), dtype=np.float32)
        self.radii = np.random.uniform(rs * 1.5, rs * 6.0, self.N).astype(np.float32)
        self.phi = np.random.uniform(0, 2 * np.pi, self.N).astype(np.float32)
        self.y_off = self.radii * np.random.uniform(-0.06, 0.06, self.N).astype(np.float32)
        self.temperature = (40000 / (self.radii / rs + 0.1)).astype(np.float32)
        
        self.update_positions()
        
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.positions.nbytes, self.positions, GL_DYNAMIC_DRAW)
        
        # Position (4 floats: x, y, z, temp)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 16, None)
        
        # Temperature (we'll pass it as a second attribute if needed, or compute in shader)
        # For simplicity, we can pass it in a combined buffer or separate. 
        # Let's pass it in a combined buffer [pos_x, pos_y, pos_z, temp]
        self.data = np.hstack([self.positions, self.temperature[:, None]])
        glBufferData(GL_ARRAY_BUFFER, self.data.nbytes, self.data, GL_DYNAMIC_DRAW)
        glEnableVertexAttribArray(1) # Temperature
        glVertexAttribPointer(1, 1, GL_FLOAT, False, 16, ctypes.c_void_p(12))

        glBindVertexArray(0)

    def update_positions(self):
        self.positions[:, 0] = self.radii * np.cos(self.phi)
        self.positions[:, 1] = self.y_off
        self.positions[:, 2] = self.radii * np.sin(self.phi)

    def update(self, dt, bh_mass, rs, G=0.5):
        # Keplerian advance: omega = sqrt(G*M/r^3)
        omega = np.sqrt(G * bh_mass / np.maximum(self.radii**3, 0.01))
        self.phi += omega * dt
        
        # Inspiral
        self.radii -= 0.005 * dt * (rs / np.maximum(self.radii, 0.1))
        
        # Respawn
        mask = self.radii < rs * 1.1
        count = np.sum(mask)
        if count > 0:
            self.radii[mask] = np.random.uniform(rs * 4.0, rs * 6.5, count)
            self.phi[mask] = np.random.uniform(0, 2 * np.pi, count)
            self.y_off[mask] = self.radii[mask] * np.random.uniform(-0.06, 0.06, count)
        
        self.temperature = (40000 / (self.radii / rs + 0.1)).astype(np.float32)
        self.update_positions()
        
        # Update VBO
        self.data = np.hstack([self.positions, self.temperature[:, None]])
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, self.data.nbytes, self.data)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.N)
        glBindVertexArray(0)
        
class ParticleSystem:
    # Generic for splash or other effects if needed, but accretion is the main one
    pass
