import numpy as np
from physics import SchwarzschildBH, Orbits, NBody
from geo import build_sphere, T, Ry, S, Rx, build_stars, build_grid
from tex import proc_earth_day, proc_earth_night, proc_clouds, proc_moon, proc_planet_rocky, proc_planet_lava
from particles import AccretionDisk
from rebirth_particles import RebirthParticles
from OpenGL.GL import *
import time

# States
NORMAL        = 0
APPROACH      = 1
MERGE_FLASH   = 2
SINGULARITY   = 3
DEVOUR        = 4
RESET         = 5
HAWKING       = 6
BIG_BANG      = 7
QUARK_PLASMA  = 8
PARTICLE_FORM = 9
NUCLEOSYNTH   = 10
DARK_AGE      = 11
FIRST_STARS   = 12
GALAXY_FORM   = 13
NEBULA        = 14
PROTOPLANETS  = 15
NEW_WORLD     = 16
IDLE_NEW      = 17

STATE_NAMES = [
    "NORMAL","APPROACH","MERGE FLASH","SINGULARITY","DEVOUR","RESET",
    "HAWKING RADIATION","BIG BANG","QUARK-GLUON PLASMA","PARTICLE FORMATION",
    "NUCLEOSYNTHESIS","COSMIC DARK AGE","FIRST STARS","GALAXY FORMATION",
    "SOLAR NEBULA","PROTOPLANETS","NEW WORLD","IDLE"
]
STATE_COLORS = [
    (0,1,0,1),(1,1,0,1),(1,1,1,1),(1,0,1,1),(1,0,0,1),(0.5,0.5,0.5,1),
    (0.6,0.1,0.9,1),(1,1,1,1),(1,0.4,0,1),(1,0.7,0.2,1),
    (1,0.55,0.25,1),(0.2,0.15,0.25,1),(0.7,0.85,1,1),(0.5,0.6,0.9,1),
    (0.9,0.2,0.1,1),(0.8,0.6,0.3,1),(0.2,0.7,1,1),(0,1,0,1)
]
PHASE_DURATIONS = [
    0, 0, 1.5, 0, 0, 0,   # 0-5
    12.0, 3.0, 5.0, 5.0,  # 6-9
    4.0, 5.0, 7.0, 8.0,   # 10-13
    6.0, 7.0, 5.0, 0       # 14-17
]
PHASE_FACTS = [
    "","","","","","",
    "Black holes slowly evaporate via quantum effects",
    "All energy and space burst from a single point",
    "Temperature exceeded 10^12 K - matter was formless",
    "Quarks bound together into protons and neutrons",
    "Hydrogen and helium nuclei formed within 3 minutes",
    "No stars existed for 150 million years",
    "Pop. III stars were 1000x more massive than our Sun",
    "Gravity along dark matter filaments built galaxies",
    "Our Sun formed from a collapsing molecular cloud",
    "Earth formed by accretion over 100 million years",
    "Life appeared ~3.8 billion years ago",
    ""
]

class GameObject:
    def __init__(self, name, vao, count, texture, pos, scale, id):
        self.name = name
        self.vao = vao
        self.count = count
        self.texture = texture
        self.pos = np.array(pos, dtype=np.float32)
        self.scale = scale
        self.id = id
        self.state = "NORMAL"
        self.stretch = 1.0
        self.compress = 1.0
        self.alpha = 1.0
        self.angular_drift = 0.0
        self.radius = scale

class Scene:
    def __init__(self, rs_mult=1.0):
        self.state = NORMAL
        self.phase_t = 0.0
        self.bh_rs = 0.0
        self.bh_rs_target = 0.0
        self.bh_pos = np.array([0, 0, 0], dtype=np.float32)
        self.flash_alpha = 0.0
        self.bh_physics = SchwarzschildBH()
        self.rs_mult = rs_mult
        self.devour_speed = 1.0
        self.rebirth_speed = 1.0

        self.objects = []
        self.planets = []
        self.stars_vao, self.stars_count = build_stars(10000)
        self.grid_vao, self.grid_count = build_grid(60, 22, 80)
        self.grid_n = 60
        self.grid_opacity = 0.5

        self.accretion_disk = None
        self.n_body = None
        self.y_off = 1.5
        self.rings = []

        # Rebirth
        self.rp = RebirthParticles(80000)
        self.bh_initial_mass = 1.0
        self.bh_mass = 1.0
        self.bh_temp = 0.0
        self.bang_radius = 0.0
        self.new_world_alpha = 0.0
        self.galaxy_rotation = 0.0
        self.star_ignitions = []

        self.init_objects()

    def init_objects(self):
        from geo import build_ring
        self.objects = []
        self.rings = []
        sphere_vao, sphere_count = build_sphere(1.0, 48, 48)
        tex_earth = proc_earth_day(1024, 512)
        self.objects.append(GameObject("Earth", sphere_vao, sphere_count, tex_earth, [0, self.y_off, 0], 1.0, 1))
        tex_moon = proc_moon(512, 256)
        self.objects.append(GameObject("Moon", sphere_vao, sphere_count, tex_moon, [3.5, self.y_off, 0], 0.27, 2))
        self.rings.append(build_ring(3.5, 128))
        self.objects.append(GameObject("ISS", sphere_vao, sphere_count, tex_moon, [1.38, self.y_off, 0], 0.05, 3))
        self.rings.append(build_ring(1.38, 64))

    def trigger_collapse(self):
        if self.state != NORMAL: return
        self.state = APPROACH
        self.phase_t = 0.0
        sphere_vao, sphere_count = build_sphere(1.0, 48, 48)
        self.planets = []
        positions = [
            [8,0,0],[-8,0,0],[0,0,8],[0,0,-8],
            [6,3,6],[-6,-3,6],[6,-3,-6],[-6,3,-6]
        ]
        colors = [
            (150,100,50),(50,150,100),(100,50,150),(200,200,100),
            (100,200,200),(200,100,200),(50,50,50),(255,128,0)
        ]
        for i, pos in enumerate(positions):
            tex = proc_planet_rocky(512,256,colors[i]) if i<7 else proc_planet_lava(512,256)
            self.planets.append(GameObject(f"P{i}", sphere_vao, sphere_count, tex, pos, 0.4+np.random.rand()*0.4, 4+i))
        masses = np.array([8.0+np.random.rand()*5 for _ in range(8)])
        pos_arr = np.array([p.pos for p in self.planets])
        vel_arr = []
        for p in self.planets:
            to_center = -p.pos / (np.linalg.norm(p.pos) + 0.1)
            vel_arr.append(to_center * 10.0)
        self.n_body = NBody(8, masses, pos_arr, np.array(vel_arr))

    def _advance_phase(self):
        self.phase_t = 0.0
        self.state += 1
        self.rp.clear()

    def _phase_dur(self):
        if self.state < len(PHASE_DURATIONS):
            return PHASE_DURATIONS[self.state] / self.rebirth_speed
        return 999

    def update(self, dt):
        self.phase_t += dt

        if self.state == NORMAL:
            t = time.time()
            self.objects[1].pos = Orbits.moon_pos(t) + np.array([0, self.y_off, 0], dtype=np.float32)
            self.objects[2].pos = Orbits.iss_pos(t) + np.array([0, self.y_off, 0], dtype=np.float32)

        elif self.state == APPROACH:
            self.n_body.step(dt * 1.5)
            for i, p in enumerate(self.planets):
                p.pos = self.n_body.positions[i].astype(np.float32)
            timeout = self.phase_t > 3.0
            collision = False
            for i, p in enumerate(self.planets):
                if np.linalg.norm(p.pos) < 0.2:
                    collision = True; break
                for j in range(i+1, len(self.planets)):
                    if np.linalg.norm(self.planets[i].pos - self.planets[j].pos) < (self.planets[i].radius + self.planets[j].radius)*0.7:
                        collision = True; break
                if collision: break
            if collision or timeout:
                self.state = MERGE_FLASH; self.phase_t = 0.0
                self.bh_rs_target = self.bh_physics.rs(np.sum(self.n_body.masses)) * self.rs_mult
                return

        elif self.state == MERGE_FLASH:
            self.flash_alpha = max(0.0, 1.0 - self.phase_t / 1.5)
            if self.phase_t > 1.5:
                self.state = SINGULARITY; self.phase_t = 0.0
                self.accretion_disk = AccretionDisk(0.1)

        elif self.state == SINGULARITY:
            self.bh_rs = self.bh_rs * 0.98 + self.bh_rs_target * 0.02
            self.accretion_disk.update(dt, self.bh_rs * 10, self.bh_rs)
            if self.bh_rs >= self.bh_rs_target * 0.95:
                self.state = DEVOUR; self.phase_t = 0.0

        elif self.state == DEVOUR:
            if self.accretion_disk:
                self.accretion_disk.update(dt, self.bh_rs * 10, self.bh_rs)
            self.bh_rs = self.bh_rs * 0.98 + self.bh_rs_target * 0.02
            targets = self.planets + self.objects[2:3] + self.objects[1:2] + self.objects[0:1]
            all_gone = True
            for obj in targets:
                if obj.state == "GONE": continue
                all_gone = False
                dist = np.linalg.norm(obj.pos - self.bh_pos)
                if obj.state == "NORMAL":
                    obj.state = "TIDAL"
                if dist < self.bh_rs * 3.0 and obj.state == "TIDAL":
                    obj.state = "INFALLING"
                if obj.state == "TIDAL":
                    d = self.bh_pos - obj.pos
                    ds = max(np.dot(d,d), 0.01)
                    obj.pos += d/np.sqrt(ds) * (5.0/np.sqrt(ds)) * self.devour_speed * dt
                    obj.stretch = 1.0 + self.phase_t * self.devour_speed * 0.3
                    obj.compress = 1.0 / np.sqrt(max(obj.stretch, 0.001))
                if obj.state == "INFALLING":
                    obj.alpha -= dt * 1.2 * self.devour_speed
                    obj.angular_drift += dt * 15.0
                    d = self.bh_pos - obj.pos
                    obj.pos += d * dt * 4.0 * self.devour_speed
                if obj.alpha <= 0.0:
                    obj.state = "GONE"
                    self.bh_rs_target += obj.scale * 0.3
            if all_gone:
                self.state = HAWKING; self.phase_t = 0.0
                self.bh_initial_mass = self.bh_rs
                self.bh_mass = self.bh_rs
                self.rp.clear()

        elif self.state == HAWKING:
            self._update_hawking(dt)

        elif self.state == BIG_BANG:
            self._update_bigbang(dt)

        elif self.state == QUARK_PLASMA:
            self._update_quark_plasma(dt)

        elif self.state == PARTICLE_FORM:
            self._update_particle_form(dt)

        elif self.state == NUCLEOSYNTH:
            self._update_nucleosynth(dt)

        elif self.state == DARK_AGE:
            self._update_dark_age(dt)

        elif self.state == FIRST_STARS:
            self._update_first_stars(dt)

        elif self.state == GALAXY_FORM:
            self._update_galaxy_form(dt)

        elif self.state == NEBULA:
            self._update_nebula(dt)

        elif self.state == PROTOPLANETS:
            self._update_protoplanets(dt)

        elif self.state == NEW_WORLD:
            self._update_new_world(dt)

        elif self.state == IDLE_NEW:
            self.reset()

    # ─── HAWKING RADIATION ───
    def _update_hawking(self, dt):
        evap = 0.08 * self.rebirth_speed
        if self.bh_mass > 0.01:
            self.bh_mass -= evap * dt / max(self.bh_mass, 0.01)
        self.bh_mass = max(self.bh_mass, 0.0)
        self.bh_rs = self.bh_mass
        frac = 1.0 - self.bh_mass / max(self.bh_initial_mass, 0.01)
        self.bh_temp = frac
        # Emit hawking particles
        rate = int(200 * (1 + frac * 3))
        if self.rp.active < 50000:
            col = [0.5+frac*0.5, 0.2+frac*0.7, 1.0, 0.8]
            self.rp.spawn_burst(min(rate, 400), self.bh_pos, (0.3,1.8), col, 2.0, 2.0+frac*2)
        self.rp.update(dt)
        if self.accretion_disk and self.bh_mass > 0.1:
            self.accretion_disk.update(dt, self.bh_mass*10, self.bh_mass)
        self.flash_alpha = 0.0
        if self.bh_mass <= 0.01 or self.phase_t >= self._phase_dur():
            self.flash_alpha = min(1.0, (self.phase_t - self._phase_dur() + 0.5) * 2)
            if self.phase_t >= self._phase_dur():
                self._advance_phase()
                self.flash_alpha = 1.0
                self.bh_rs = 0; self.accretion_disk = None

    # ─── BIG BANG ───
    def _update_bigbang(self, dt):
        dur = self._phase_dur()
        t = self.phase_t / dur
        self.flash_alpha = max(0.0, 1.0 - self.phase_t * 2.0)
        self.bang_radius = (t ** 0.35) * 8.0
        if self.phase_t < 0.1:
            self.rp.spawn_burst(2000, [0,0,0], (2,12), [1,0.95,0.6,1], 3.0, 3.0)
        self.rp.update(dt)
        if self.phase_t >= dur:
            self._advance_phase()

    # ─── QUARK PLASMA ───
    def _update_quark_plasma(self, dt):
        dur = self._phase_dur()
        if self.phase_t < dt * 2:
            self.rp.spawn_sphere(30000, 6.0, [1,0.6,0.1,0.8], 0.002, dur, 3.0)
        self.rp.update(dt)
        # Cool: shift colours
        t = self.phase_t / dur
        for i in range(self.rp.active):
            self.rp.col[i, 0] = 1.0
            self.rp.col[i, 1] = max(0.1, 0.6 - t*0.4)
            self.rp.col[i, 2] = max(0.0, 0.1 - t*0.1)
        if self.phase_t >= dur: self._advance_phase()

    # ─── PARTICLE FORMATION ───
    def _update_particle_form(self, dt):
        dur = self._phase_dur()
        t = self.phase_t / dur
        self.rp.attract([0,0,0], 0.3, dt)
        self.rp.update(dt)
        # Colour shift to distinct reds and blues
        for i in range(min(self.rp.active, 2000)):
            self.rp.col[i] = [1.0, 0.4, 0.1, 0.9]  # proton
        for i in range(2000, min(self.rp.active, 4000)):
            self.rp.col[i] = [0.4, 0.6, 0.9, 0.9]  # neutron
        if self.phase_t >= dur: self._advance_phase()

    # ─── NUCLEOSYNTHESIS ───
    def _update_nucleosynth(self, dt):
        dur = self._phase_dur()
        t = self.phase_t / dur
        self.rp.attract([0,0,0], 0.1, dt)
        self.rp.update(dt)
        # CMB flash at t=0.5
        if 0.45 < t < 0.55:
            self.flash_alpha = max(0, 1.0 - abs(t-0.5)*20)
        else:
            self.flash_alpha = 0
        # Fade particles at end
        if t > 0.7:
            for i in range(self.rp.active):
                self.rp.col[i, 3] *= 0.98
        if self.phase_t >= dur: self._advance_phase(); self.flash_alpha = 0

    # ─── DARK AGE ───
    def _update_dark_age(self, dt):
        dur = self._phase_dur()
        t = self.phase_t / dur
        if self.phase_t < dt * 2:
            self.rp.clear()
            self.rp.spawn_sphere(3000, 8.0, [0.15,0.12,0.10,0.15], 0.001, dur, 1.5)
        self.rp.update(dt)
        if self.phase_t >= dur: self._advance_phase()

    # ─── FIRST STARS ───
    def _update_first_stars(self, dt):
        dur = self._phase_dur()
        t = self.phase_t / dur
        # Ignite stars at intervals
        n_stars = int(t * 12)
        while len(self.star_ignitions) < n_stars:
            pos = np.random.uniform(-5, 5, 3).astype(np.float32)
            self.star_ignitions.append({'pos': pos, 't': self.phase_t, 'scale': 0.0})
        for s in self.star_ignitions:
            age = self.phase_t - s['t']
            s['scale'] = min(0.15, age * 0.5)
        self.rp.update(dt)
        if self.phase_t >= dur:
            self._advance_phase()
            self.galaxy_rotation = 0.0

    # ─── GALAXY FORMATION ───
    def _update_galaxy_form(self, dt):
        dur = self._phase_dur()
        t = self.phase_t / dur
        if self.phase_t < dt * 2:
            self.rp.clear()
            # Spiral arms
            n = 20000
            theta = np.random.uniform(0, 4*np.pi, n).astype(np.float32)
            arm = np.random.randint(0, 2, n) * np.pi
            r = 0.3 * np.exp(0.15 * theta)
            x = r * np.cos(theta + arm) + np.random.normal(0, 0.1, n)
            z = r * np.sin(theta + arm) + np.random.normal(0, 0.1, n)
            y = np.random.normal(0, 0.05, n)
            positions = np.stack([x, y, z], axis=1).astype(np.float32)
            vels = np.zeros((n, 3), dtype=np.float32)
            bright = np.clip(1.0 / (r + 0.1) * 0.3, 0, 1)
            cols = np.zeros((n, 4), dtype=np.float32)
            cols[:, 0] = 0.8 + bright * 0.2
            cols[:, 1] = 0.85 + bright * 0.15
            cols[:, 2] = 0.6 + bright * 0.4
            cols[:, 3] = 0.8
            lifetimes = np.full(n, dur + 5, dtype=np.float32)
            sizes = np.full(n, 2.0, dtype=np.float32)
            sizes[bright > 0.5] = 3.5
            self.rp.spawn(n, positions, vels, cols, lifetimes, sizes)
        self.galaxy_rotation += dt * 0.3
        self.rp.orbit_advance(dt, 0.5)
        self.rp.update(dt)
        if self.phase_t >= dur: self._advance_phase()

    # ─── NEBULA ───
    def _update_nebula(self, dt):
        dur = self._phase_dur()
        t = self.phase_t / dur
        if self.phase_t < dt * 2:
            self.rp.clear()
            # H emission
            self.rp.spawn_sphere(40000, 4.0, [0.9,0.1,0.1,0.5], 0.0, dur, 2.0)
            # OIII emission
            self.rp.spawn_sphere(15000, 3.5, [0.1,0.8,0.6,0.4], 0.0, dur, 1.5)
            # Dust
            self.rp.spawn_sphere(5000, 3.0, [0.2,0.1,0.05,0.3], 0.0, dur, 1.0)
        # Collapse
        self.rp.attract([0,0,0], 2.0 * t, dt)
        self.rp.flatten_y(0.98)
        self.rp.update(dt)
        if self.phase_t >= dur: self._advance_phase()

    # ─── PROTOPLANETS ───
    def _update_protoplanets(self, dt):
        dur = self._phase_dur()
        t = self.phase_t / dur
        if self.phase_t < dt * 2:
            self.rp.clear()
            self.rp.spawn_disk(20000, 0.2, 3.0, 0.05,
                               [1.0,0.5,0.1,0.7], [0.3,0.3,0.8,0.5], dur, 2.0)
        self.rp.orbit_advance(dt, 2.0)
        self.rp.update(dt)
        # Moon impact flash at t=0.65
        if 0.63 < t < 0.67:
            self.flash_alpha = max(0, 1.0 - abs(t-0.65)*30)
        else:
            self.flash_alpha = 0
        if self.phase_t >= dur: self._advance_phase(); self.flash_alpha = 0

    # ─── NEW WORLD ───
    def _update_new_world(self, dt):
        dur = self._phase_dur()
        t = self.phase_t / dur
        self.new_world_alpha = min(1.0, t * 2.0)
        self.rp.update(dt)
        if self.phase_t >= dur:
            self.state = IDLE_NEW; self.phase_t = 0

    def skip_phase(self):
        if HAWKING <= self.state <= NEW_WORLD:
            self._advance_phase()
            if self.state > NEW_WORLD:
                self.state = IDLE_NEW

    def reset(self):
        self.state = NORMAL
        self.phase_t = 0.0
        self.bh_rs = 0.0
        self.bh_rs_target = 0.0
        self.bh_pos = np.array([0, 0, 0], dtype=np.float32)
        self.flash_alpha = 0.0
        self.bh_mass = 0; self.bh_temp = 0; self.bang_radius = 0
        self.new_world_alpha = 0; self.galaxy_rotation = 0
        self.star_ignitions = []
        self.init_objects()
        self.planets = []
        self.accretion_disk = None
        self.rp.clear()
