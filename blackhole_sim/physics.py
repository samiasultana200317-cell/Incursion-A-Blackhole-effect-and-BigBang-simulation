import numpy as np

class NBody:
    def __init__(self, n, masses, positions, velocities):
        self.n = n
        self.masses = masses.astype(np.float64)
        self.positions = positions.astype(np.float64)
        self.velocities = velocities.astype(np.float64)
        self.G = 0.5
        self.softening = 0.1

    def acceleration(self, pos):
        r = pos[:, None, :] - pos[None, :, :] # (N, N, 3)
        d2 = (r**2).sum(axis=2) + self.softening**2
        d3 = d2 * np.sqrt(d2)
        # a = G * M * r / r^3
        # We need to broadcast mass: masses[None, :, None]
        inv_d3 = 1.0 / d3
        np.fill_diagonal(inv_d3, 0)
        a = (self.G * self.masses[None, :, None] * r * inv_d3[:, :, None]).sum(axis=1) # Note: r is pos_j - pos_i if we want force on i
        # Actually r = pos_j - pos_i. Correct: (pos[j] - pos[i])
        # So a_i = sum_j (G * m_j * (pos_j - pos_i) / |pos_j - pos_i|^3)
        return a

    def step(self, dt):
        # Velocity Verlet
        a0 = self.acceleration(self.positions)
        self.positions += self.velocities * dt + 0.5 * a0 * dt**2
        a1 = self.acceleration(self.positions)
        self.velocities += 0.5 * (a0 + a1) * dt

class SchwarzschildBH:
    def __init__(self):
        self.G_scaled = 0.5
        self.c_scaled = 5.0

    def rs(self, mass):
        return 2.0 * self.G_scaled * mass / (self.c_scaled**2)

    def tidal_force(self, bh_mass, obj_pos, bh_pos, obj_radius):
        r = np.linalg.norm(obj_pos - bh_pos)
        return 2.0 * self.G_scaled * bh_mass * obj_radius / max(r**3, 0.001)

    def orbital_speed(self, bh_mass, radius):
        return np.sqrt(self.G_scaled * bh_mass / max(radius, 0.01))

class Orbits:
    @staticmethod
    def moon_pos(t, speed=1.0):
        period = 27.0
        a = t * speed * 2 * np.pi / period
        tilt = np.radians(5.14)
        r = 3.5
        return np.array([r * np.cos(a), r * np.sin(a) * np.sin(tilt), r * np.sin(a) * np.cos(tilt)], dtype=np.float32)

    @staticmethod
    def iss_pos(t, speed=1.0):
        period = 10.0
        a = t * speed * 2 * np.pi / period
        tilt = np.radians(51.6)
        r = 1.38
        return np.array([r * np.cos(a), r * np.sin(a) * np.sin(tilt), r * np.sin(a) * np.cos(tilt)], dtype=np.float32)
