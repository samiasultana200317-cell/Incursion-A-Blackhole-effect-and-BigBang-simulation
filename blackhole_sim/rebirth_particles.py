import numpy as np
from OpenGL.GL import *
import ctypes

class RebirthParticles:
    """Unified particle system for all rebirth phases. Pool-based with dynamic subranges."""
    def __init__(self, max_n=80000):
        self.N = max_n
        self.active = 0
        self.pos = np.zeros((max_n, 3), dtype=np.float32)
        self.vel = np.zeros((max_n, 3), dtype=np.float32)
        self.col = np.ones((max_n, 4), dtype=np.float32)   # rgba
        self.life = np.zeros(max_n, dtype=np.float32)
        self.max_life = np.ones(max_n, dtype=np.float32)
        self.size = np.full(max_n, 2.0, dtype=np.float32)

        # GPU buffers: interleaved [pos(3), col(4), size(1)] = 8 floats = 32 bytes
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, max_n * 32, None, GL_DYNAMIC_DRAW)
        # pos
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 32, None)
        # col
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 4, GL_FLOAT, False, 32, ctypes.c_void_p(12))
        # size
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 1, GL_FLOAT, False, 32, ctypes.c_void_p(28))
        glBindVertexArray(0)

    def clear(self):
        self.active = 0

    def spawn(self, n, positions, velocities, colors, lifetimes, sizes):
        end = min(self.active + n, self.N)
        actual = end - self.active
        if actual <= 0: return
        s = self.active
        self.pos[s:end] = positions[:actual]
        self.vel[s:end] = velocities[:actual]
        self.col[s:end] = colors[:actual]
        self.life[s:end] = 0.0
        self.max_life[s:end] = lifetimes[:actual]
        self.size[s:end] = sizes[:actual]
        self.active = end

    def spawn_burst(self, n, origin, vel_range, color, life, sz=2.0):
        dirs = np.random.randn(n, 3).astype(np.float32)
        norms = np.linalg.norm(dirs, axis=1, keepdims=True) + 1e-6
        dirs /= norms
        speeds = np.random.uniform(vel_range[0], vel_range[1], (n, 1)).astype(np.float32)
        vels = dirs * speeds
        positions = np.broadcast_to(np.array(origin, dtype=np.float32), (n, 3)).copy()
        colors = np.broadcast_to(np.array(color, dtype=np.float32), (n, 4)).copy()
        lifetimes = np.full(n, life, dtype=np.float32)
        sizes = np.full(n, sz, dtype=np.float32)
        self.spawn(n, positions, vels, colors, lifetimes, sizes)

    def spawn_sphere(self, n, radius, color, vel_scale=0.01, life=10.0, sz=2.0):
        dirs = np.random.randn(n, 3).astype(np.float32)
        norms = np.linalg.norm(dirs, axis=1, keepdims=True) + 1e-6
        dirs /= norms
        r = np.random.uniform(0, radius, (n, 1)).astype(np.float32) ** (1.0/3.0) * radius
        positions = dirs * r
        vels = dirs * vel_scale
        colors = np.broadcast_to(np.array(color, dtype=np.float32), (n, 4)).copy()
        # slight color variation
        colors[:, :3] += np.random.uniform(-0.05, 0.05, (n, 3)).astype(np.float32)
        colors = np.clip(colors, 0, 1)
        lifetimes = np.full(n, life, dtype=np.float32)
        sizes = np.full(n, sz, dtype=np.float32)
        self.spawn(n, positions, vels, colors, lifetimes, sizes)

    def spawn_disk(self, n, inner_r, outer_r, y_spread, color_inner, color_outer, life=10.0, omega_base=1.0):
        radii = np.random.uniform(inner_r, outer_r, n).astype(np.float32)
        phi = np.random.uniform(0, 2*np.pi, n).astype(np.float32)
        y = np.random.uniform(-y_spread, y_spread, n).astype(np.float32)
        positions = np.zeros((n, 3), dtype=np.float32)
        positions[:, 0] = radii * np.cos(phi)
        positions[:, 1] = y
        positions[:, 2] = radii * np.sin(phi)
        # Keplerian velocity
        omega = omega_base / np.sqrt(np.maximum(radii, 0.1))
        vels = np.zeros((n, 3), dtype=np.float32)
        vels[:, 0] = -np.sin(phi) * omega * radii
        vels[:, 2] = np.cos(phi) * omega * radii
        # Color blend by radius
        t = ((radii - inner_r) / max(outer_r - inner_r, 0.01))[:, None]
        ci = np.array(color_inner, dtype=np.float32)
        co = np.array(color_outer, dtype=np.float32)
        colors = ci * (1 - t) + co * t
        lifetimes = np.full(n, life, dtype=np.float32)
        sizes = np.full(n, 2.0, dtype=np.float32)
        self.spawn(n, positions, vels, colors, lifetimes, sizes)

    def update(self, dt):
        if self.active == 0: return
        s = slice(0, self.active)
        self.pos[s] += self.vel[s] * dt
        self.life[s] += dt
        # Fade alpha near end of life
        t = self.life[s] / np.maximum(self.max_life[s], 0.01)
        self.col[s, 3] = np.clip(1.0 - t, 0, 1)
        # Remove dead
        alive = self.life[:self.active] < self.max_life[:self.active]
        n_alive = int(np.sum(alive))
        if n_alive < self.active:
            self.pos[:n_alive] = self.pos[:self.active][alive]
            self.vel[:n_alive] = self.vel[:self.active][alive]
            self.col[:n_alive] = self.col[:self.active][alive]
            self.life[:n_alive] = self.life[:self.active][alive]
            self.max_life[:n_alive] = self.max_life[:self.active][alive]
            self.size[:n_alive] = self.size[:self.active][alive]
            self.active = n_alive

    def attract(self, center, strength, dt):
        if self.active == 0: return
        s = slice(0, self.active)
        d = np.array(center, dtype=np.float32) - self.pos[s]
        dist = np.linalg.norm(d, axis=1, keepdims=True) + 0.1
        self.vel[s] += d / dist * strength * dt / dist

    def flatten_y(self, factor):
        if self.active == 0: return
        self.vel[:self.active, 1] *= factor

    def orbit_advance(self, dt, omega_scale=1.0):
        if self.active == 0: return
        s = slice(0, self.active)
        r = np.sqrt(self.pos[s, 0]**2 + self.pos[s, 2]**2) + 0.01
        omega = omega_scale / np.sqrt(r)
        dphi = omega * dt
        cos_d = np.cos(dphi); sin_d = np.sin(dphi)
        x = self.pos[s, 0]; z = self.pos[s, 2]
        self.pos[s, 0] = x * cos_d - z * sin_d
        self.pos[s, 2] = x * sin_d + z * cos_d

    def upload(self):
        if self.active == 0: return
        n = self.active
        data = np.empty((n, 8), dtype=np.float32)
        data[:, :3] = self.pos[:n]
        data[:, 3:7] = self.col[:n]
        data[:, 7] = self.size[:n]
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, data.nbytes, data)

    def draw(self):
        if self.active == 0: return
        self.upload()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.active)
        glBindVertexArray(0)
