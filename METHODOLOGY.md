# INCURSION-2: EXACT METHODOLOGY DESIGN

**Project:** Black Hole Simulator  
**Type:** Educational Physics Visualization Engine  
**Approach:** Real-time Interactive Simulation with Advanced Rendering  
**Version:** 1.0 (Academic/Production-Ready)

---

## 1. EXECUTIVE METHODOLOGY OVERVIEW

Incursion-2 employs a **layered, modular architecture** combining:

1. **State Machine-Driven Simulation** (18 distinct phases)
2. **Physics-Accurate N-Body + Schwarzschild Dynamics**
3. **Advanced HDR Rendering Pipeline** (deferred shading, bloom, lensing)
4. **Data-Driven Particle Systems** (30K accretion disk + rebirth effects)
5. **Real-Time Interactive Controls** (camera, physics pacing, diagnostics)

**Core Principle:** Separate concerns into independent modules that communicate through physics state and scene objects, allowing rapid iteration and validation.

---

## 2. ARCHITECTURE LAYERS

### 2.1 Input Layer (User Interaction)

**Inputs:** Keyboard, Mouse, ImGui Controls

| Input | Outcome | Module |
|-------|---------|--------|
| Left Mouse Drag | Orbit camera | camera.py |
| Mouse Scroll | Zoom in/out | camera.py |
| Left Mouse Click | Ray-cast to pick object | picker.py |
| SPACE | Trigger collapse / Reset | scene.py (state machine) |
| R | Force reset to NORMAL | scene.py |
| N | Skip to next phase | scene.py |
| C | Cycle camera modes | camera.py |
| ImGui Sliders | Adjust physics/rendering parameters | main.py |

**Key Design:** Input is non-blocking; all user actions queue state changes processed in the next physics update.

---

### 2.2 Logic Layer (Decision + Computation)

**Modules:**
- **Scene Manager (scene.py):** 18-state finite state machine orchestrating simulation phases
- **Physics Engine (physics.py):** N-body gravity, Schwarzschild calculations, collision detection
- **Camera System (camera.py):** View matrix computation, smooth transitions
- **Picker (picker.py):** Mouse ray-casting, RTT object ID readback

**Flow:**
```
Input → Scene.update(dt) → Check state → Branch to phase-specific logic
    ↓
Physics.step(dt) → Compute forces → Integrate → Detect collisions
    ↓
Camera.update() → Compute view/projection matrices
    ↓
State: Ready for rendering
```

---

### 2.3 Data Layer (Simulation State)

**Core Data Structures:**

```python
class GameObject:
    position: np.array(3,)      # World XYZ
    velocity: np.array(3,)      # Velocity vector
    mass: float                 # Mass for gravity
    radius: float               # Collision sphere
    lifecycle_state: Enum       # NORMAL, TIDAL, INFALLING, GONE
    color: np.array(4,)         # RGBA

class BlackHole:
    position: np.array(3,)
    mass: float
    radius: float               # Schwarzschild radius
    accretion_mass_rate: float

class AccretionDisk:
    particles: np.array(N, 3)   # 30,000 positions
    radii: np.array(N,)         # Distance from black hole
    angles: np.array(N,)        # Angular position
    temperatures: np.array(N,)  # Thermal value
    vbo: GLuint                 # GPU buffer
```

**Update Frequency:** Every frame (60 FPS nominal)

---

### 2.4 Rendering Layer (Graphics)

**Modules:**
- **Shader Manager (shader.py):** GLSL compilation, uniform data streaming
- **HDR Pipeline (hdr.py):** Multi-render targets, framebuffer management
- **Geometry Generator (geo.py):** Procedural mesh generation (spheres, grids)
- **Texture Generator (tex.py):** Procedural textures (FBM noise, planetary surfaces)

**Rendering Flow:**
```
Bind HDR FBO (3 attachments)
  → Render all objects to MRT
    → Lensing post-process
    → Bloom post-process
    → Composite (tone-map + gamma)
    → Display
```

---

### 2.5 Output Layer (Display)

**Final Steps:**
1. Combine lensed scene + bloom
2. Apply Reinhard tone-mapping: `hdr / (hdr + 1.0)`
3. Apply gamma correction: `pow(result, 1.0/2.2)`
4. Blend ImGui overlay
5. Swap buffers to screen

---

## 3. 18-PHASE STATE MACHINE METHODOLOGY

### 3.1 Phase Progression (Detailed Flowchart)

```
PHASE 0: NORMAL
├─ Duration: ∞ (user-triggered)
├─ Object Dynamics: Analytic orbits
│  ├─ Moon: 27-day period, 3.5 unit radius, 5.14° inclination
│  └─ ISS: 10-day period, 1.38 unit radius, 51.6° inclination
├─ Rendering: Normal scene with grid
└─ User Action: SPACE → Phase 1

PHASE 1: APPROACH
├─ Duration: 3-8 seconds (collision or timeout)
├─ Object Dynamics: 8 planets spawn at formation ~6-8 units
│  ├─ Mass: 8-13 solar units each
│  ├─ Force Calculation: O(N²) all-pairs gravity
│  ├─ Integration: Velocity Verlet, dt × 1.5 (accelerated)
│  └─ Collision Detection: if distance < (r1+r2)×0.7 → merge
├─ Timeout: if >3 sec → force merge anyway
└─ Outcome: → Phase 2

PHASE 2: MERGE_FLASH
├─ Duration: 1.5 seconds
├─ Visual: Screen flash, particle burst
├─ Physics: Stationary (all objects frozen)
└─ Outcome: → Phase 3 (automatic)

PHASE 3: SINGULARITY
├─ Duration: User-determined (objects still infalling)
├─ Black Hole Formation:
│  ├─ Position: Mass-weighted centroid of 8 planets
│  ├─ Initial Mass: Sum of all planet masses
│  ├─ Schwarzschild Radius: Rs = 2GM/c² (G=0.5, c=5.0)
│  └─ Growth: rs_new = rs × 0.98 + target × 0.02 (smooth interpolation)
├─ Accretion Disk Spawn:
│  ├─ 30,000 particles generated
│  ├─ Radial distribution: uniform [Rs×1.5, Rs×6.0]
│  ├─ Angular distribution: uniform [0, 2π]
│  ├─ Vertical offset: ±6% of radius (thin disk)
│  └─ Initial temperature: T = 40000K / (radius/Rs)
├─ Grid Deformation: Spacetime grid warps around BH
└─ User Observation: Watch accretion form

PHASE 4: DEVOUR
├─ Duration: Varies per object (~5-15 sec total)
├─ Per-Object Lifecycle:
│  ├─ State: NORMAL (outside tidal radius)
│  ├─ State: TIDAL (inside tidal radius, stretch begins)
│  │   - Tidal Force: F = 2GM_BH × r_obj / r_to_BH³
│  │   - Radial Stretch: s = 1 + F × elapsed_time × devour_speed
│  │   - Lateral Compress: c = 1 / √s
│  │   - Spiral rate: φ_drift += orbital_speed × dt
│  ├─ State: INFALLING (inside Rs×2, fade begins)
│  │   - Alpha: 1 - elapsed_time × 0.3 × devour_speed
│  │   - Heat glow: blend toward (1.0, 0.5, 0.1)
│  └─ State: GONE (alpha = 0, removed from scene)
├─ Accretion Disk: Particles continue Keplerian motion
│  ├─ Inspiraling: r -= 0.005 × dt × (Rs/r)
│  ├─ Respawn: Particles at Rs×1.1 repositioned to Rs×6.0
│  └─ Temperature recalc: T = 40000K / (current_r/Rs)
└─ Outcome: → Phase 5 (when all objects consumed)

PHASE 5: RESET
├─ Duration: Instant
├─ Actions:
│  ├─ Clear all game objects
│  ├─ Reset black hole
│  ├─ Reset accretion disk
│  └─ Clear particles
└─ Outcome: → Phase 6 (automatic)

PHASE 6-17: HAWKING → NUCLEOSYNTH → GALAXY_FORM → NEW_WORLD
├─ Methodology: Linear timeline with phase-specific particle effects
├─ Each phase duration: 3-12 seconds (configurable via rebirth_speed slider)
│
├─ PHASE 6 (HAWKING, 12 sec):
│  ├─ Black hole radiates, temperature rises
│  ├─ Particle effect: Subtle glow increase
│  └─ → Phase 7
│
├─ PHASE 7 (BIG_BANG, 3 sec):
│  ├─ Final explosion from quantum singularity
│  ├─ Particle effect: Burst pattern from origin
│  └─ → Phase 8
│
├─ PHASE 8 (QUARK_PLASMA, 5 sec):
│  ├─ Extreme energy, elementary particles
│  ├─ Particle effect: Expanding sphere of plasma
│  └─ → Phase 9
│
├─ PHASE 9 (PARTICLE_FORM, 5 sec):
│  ├─ Quarks bind into hadrons
│  ├─ Particle effect: Cooling, density increase
│  └─ → Phase 10
│
├─ PHASE 10 (NUCLEOSYNTH, 4 sec):
│  ├─ Proton/neutron formation
│  ├─ Particle effect: Disk rotation pattern
│  └─ → Phase 11
│
├─ PHASE 11 (DARK_AGE, 5 sec):
│  ├─ Cosmic dark ages, minimal light
│  ├─ Rendering: Low ambient, dark atmosphere
│  ├─ Particle effect: Minimal, cold coloring
│  └─ → Phase 12
│
├─ PHASE 12 (FIRST_STARS, 7 sec):
│  ├─ Population III stars ignite
│  ├─ Particle effect: Star bursts scattered
│  └─ → Phase 13
│
├─ PHASE 13 (GALAXY_FORM, 8 sec):
│  ├─ Galactic structures emerge
│  ├─ Particle effect: Spiral galaxy pattern
│  └─ → Phase 14
│
├─ PHASE 14 (NEBULA, 6 sec):
│  ├─ Solar nebula collapse
│  ├─ Particle effect: Rotating disk, colored clouds
│  └─ → Phase 15
│
├─ PHASE 15 (PROTOPLANETS, 7 sec):
│  ├─ Planetesimals form from accretion
│  ├─ Particle effect: Disk particles clumping patterns
│  └─ → Phase 16
│
├─ PHASE 16 (NEW_WORLD, 5 sec):
│  ├─ Terraformed Earth forms
│  ├─ Rendering: New Earth appears, Moon forms
│  ├─ Particle effect: Settling, debris clearing
│  └─ → Phase 17
│
└─ PHASE 17 (IDLE_NEW, ∞):
    ├─ Universe finished
    ├─ User can trigger reset (R key) → Phase 0
    └─ or observe new solar system
```

**State Machine Parameters:**
```python
class SceneState(Enum):
    NORMAL, APPROACH, MERGE_FLASH, SINGULARITY,
    DEVOUR, RESET, HAWKING, BIG_BANG, QUARK_PLASMA,
    PARTICLE_FORM, NUCLEOSYNTH, DARK_AGE, FIRST_STARS,
    GALAXY_FORM, NEBULA, PROTOPLANETS, NEW_WORLD, IDLE_NEW
```

---

## 4. PHYSICS SIMULATION METHODOLOGY

### 4.1 N-Body Gravity (Newtonian)

**Algorithm:** Velocity Verlet Integration (2nd order, error O(dt³))

**Force Calculation:**
```
For each object i:
    a_i = 0
    For each object j ≠ i:
        r_ij = pos_j - pos_i
        dist = ||r_ij|| + softening(ε = 0.1)
        F_ij = (G × m_i × m_j) / dist²
        a_i += F_ij × normalize(r_ij)
```

**Integration Step (per frame at dt):**
```
v_half = v + a × (dt / 2)
pos_new = pos + v_half × dt
a_new = compute_acceleration(pos_new)
v_new = v_half + a_new × (dt / 2)
```

**Configuration:**
- **G (Gravitational Constant):** 0.5 (visual scaling)
- **c (Speed of Light):** 5.0 (visual scaling)
- **Softening (ε):** 0.1 (prevent singularities during close approaches)

---

### 4.2 Schwarzschild Black Hole Physics

**Event Horizon Calculation:**
```
Rs = (2 × G × M_BH) / c²

With our constants (G=0.5, c=5.0):
Rs = 2 × 0.5 × M_BH / 25 = 0.04 × M_BH
```

**Tidal Force Calculation:**
```
For object at position p inside tidal sphere:
    r_to_BH = pos_BH - pos_obj
    r_dist = ||r_to_BH||
    
    F_tidal = (2 × G × M_BH × object_radius) / (r_dist³)
    
Stretches object along radial axis (spaghettification)
```

**Spaghettification Deformation:**
```
stretch_factor = 1 + F_tidal × elapsed_time × devour_speed
compress_factor = 1 / sqrt(stretch_factor)

In vertex shader:
    radial_component = (dot(v, toBH) / |toBH|) × stretching
    lateral_component = (v - radial) × compression
    deformed_v = radial_component + lateral_component
```

---

### 4.3 Accretion Disk Dynamics (Keplerian Orbits)

**Particle Initialization (Phase 3):**
```python
num_particles = 30,000

for each particle:
    radius = random_uniform(Rs × 1.5, Rs × 6.0)
    angle = random_uniform(0, 2π)
    height = random_uniform(-0.06×radius, +0.06×radius)
    
    position = [
        radius × cos(angle),
        height,
        radius × sin(angle)
    ]
    
    temperature = 40000 / (radius / Rs)  # Hotter near BH
```

**Per-Frame Update:**
```python
for each particle:
    # Keplerian orbital angular velocity
    omega = sqrt(G × M_BH / (radius³))
    angle += omega × dt
    
    # Inspiral (accretion inward)
    radius -= 0.005 × dt × (Rs / radius)
    
    # Respawn if crossed event horizon
    if radius < Rs:
        radius = Rs × 6.0
        angle = random_uniform(0, 2π)
    
    # Update position
    position = [
        radius × cos(angle),
        height,
        radius × sin(angle)
    ]
```

**GPU Streaming:**
- All 30K particle positions streamed to VBO every frame
- Shader reads temperature, computes color via black-body mapping

---

### 4.4 Collision Detection & Merging

**APPROACH Phase Collision Check:**
```python
for i, planet_i in enumerate(planets):
    for j, planet_j in enumerate(planets[i+1:]):
        dist = ||planet_i.pos - planet_j.pos||
        collision_dist = (planet_i.radius + planet_j.radius) × 0.7
        
        if dist < collision_dist:
            trigger_merge()
            return
```

**Merge Operation:**
```python
# Mass-weighted centroid
new_position = sum(m_i × pos_i) / sum(m_i)
new_mass = sum(m_i)
new_radius = cbrt(new_mass)  # Scale volume appropriately

# Momentum conservation
new_velocity = sum(m_i × v_i) / sum(m_i)
```

---

## 5. RENDERING PIPELINE METHODOLOGY

### 5.1 Deferred Rendering Architecture

**Multi-Render Target (MRT) Setup:**

```
┌─ Attachment 0: Scene Color
│   └─ Format: GL_RGBA16F (16-bit float HDR)
│   └─ Content: All rendered objects
│
├─ Attachment 1: Bright Pass
│   └─ Format: GL_RGBA16F (16-bit float HDR)
│   └─ Content: Bloom sources (bright pixels)
│
├─ Attachment 2: Object ID
│   └─ Format: GL_RGBA32F (single float per pixel)
│   └─ Content: Unique object ID for picking
│
└─ Depth: GL_DEPTH24_STENCIL8 (renderbuffer)
```

**Rendering Process:**

1. **Bind Scene FBO** (all 3 MRTs active)
2. **Clear all attachments** (color=black, ID=-1)
3. **Render all geometry** in order:
   - **Stars:** Point sprites (star shader)
   - **Space-time Grid:** Deforming mesh (grid shader)
   - **Earth:** Textured sphere (earth shader)
   - **Moon:** Textured sphere (moon shader)
   - **ISS/Satellites:** Small spheres (obj shader)
   - **Demo Planets:** UV spheres (obj shader)
   - **Black Hole:** UV sphere, inward normals (blackhole shader)
   - **Accretion Disk:** GPU particle stream (accretion shader)
4. **Unbind Scene FBO**

---

### 5.2 Post-Processing Pipeline (3 Passes)

#### **Pass 1: Gravitational Lensing**

**Purpose:** Simulate photon bending near event horizon

**Algorithm (Screen-Space):**
```glsl
vec2 screenCoord = gl_FragCoord.xy / windowSize;
vec2 bhScreenPos = project(bh_world_pos);
vec2 toCenter = bhScreenPos - screenCoord;
float distance = length(toCenter);

// UV distortion strength proportional to inverse distance
float theta = uRsScreen / (distance + 0.001);
vec2 deflect = normalize(toCenter) * theta * uLensingStrength;

// Sample lensed scene
vec3 lensed = texture(uSceneTexture, screenCoord + deflect).rgb;

// Add Einstein ring brightening
float ringBrightness = smoothstep(uRsScreen * 0.9, uRsScreen, distance) 
                     - smoothstep(uRsScreen, uRsScreen * 1.1, distance);
lensed += vec3(1.0, 0.8, 0.4) * ringBrightness * 2.0;
```

**Output:** `lens_fbo` (texture for next pass)

---

#### **Pass 2: Bloom (Separable Gaussian Blur)**

**Purpose:** Add glow to bright objects

**Algorithm (8 iterations, ping-pong):**
```
For i = 0 to 7:
    horizontal_blur(bright_texture[i], temp)
    vertical_blur(temp, bright_texture[i+1])
    
Final bloom texture = bright_texture[8]
```

**Gaussian Kernel (1D, 5 taps):**
```glsl
weights = [0.06136, 0.24477, 0.38774, 0.24477, 0.06136]
offsets = [-2, -1, 0, 1, 2]

result = sum(weights[i] * sample(tex, coord + offset[i] * pixelSize))
```

**Output:** `bloom_fbo`

---

#### **Pass 3: Composite & Tone-Mapping**

**Inputs:**
- Lensed scene (from Pass 1)
- Bloom result (from Pass 2)

**Algorithm:**
```glsl
// Combine lensed + bloom
vec3 hdr = lensed + bloom * uBloomStrength;

// Reinhard tone-mapping
vec3 mapped = hdr / (hdr + 1.0);

// Gamma correction
vec3 result = pow(mapped, vec3(1.0 / 2.2));

// Final output to default framebuffer
gl_FragColor = vec4(result, 1.0);
```

**Key Benefits:**
- HDR prevents clipping on bright sources
- Reinhard mapping compresses highlights gracefully
- Gamma correction achieves perceptual linearity on sRGB displays

---

### 5.3 Shader Techniques Summary

| Shader | Purpose | Key Technique |
|--------|---------|----------------|
| **obj.vert/frag** | Generic PBR metallic | Fresnel, roughness, normal mapping |
| **earth.frag** | Earth day/night blending | Texture blend based on light angle |
| **moon.frag** | Lunar surface | Grayscale + bump mapping |
| **grid.vert/frag** | Spacetime deformation | Per-vertex gravity well displacement |
| **blackhole.vert/frag** | Event horizon rendering | Inward normals, procedural bands |
| **accretion.frag** | Accretion disk particles | Black-body temperature coloring, size scaling |
| **devour.vert/frag** | Spaghettification animation | Radial/lateral deformation + heat glow |
| **stars.vert/frag** | Starfield | Point sprite expansion, distance attenuation |
| **blur.vert/frag** | Gaussian blur | Separable kernel (ping-pong) |
| **lensing.frag** | Gravitational UV distortion | Screen-space distortion field |
| **composite.frag** | Tone-mapping | Reinhard + gamma correction |
| **plasma.frag** | Quantum plasma effects | Procedural noise, energy visualization |
| **rebirth.vert/frag** | Rebirth particle effects | Phase-specific color/behavior |
| **bang.vert/frag** | Big Bang explosion | Radial burst pattern, fade-out |
| **galaxy.vert/frag** | Galaxy formation | Spiral pattern with dust lanes |

---

## 6. PARTICLE SYSTEMS METHODOLOGY

### 6.1 Accretion Disk (30K Particles - GPU-Driven)

**Lifecycle:**

```
Spawn (Phase 3)
    ↓
Keplerian Motion (Phases 3-4)
    ├─ Orbital revolution: angle += ω·dt
    ├─ Inspiraling: radius -= 0.005·dt·(Rs/r)
    └─ Temperature: T = 40000K/(r/Rs)
    ↓
Respawn at Event Horizon (automatic)
    └─ if radius < Rs → reset to Rs×6.0
```

**Rendering (per particle):**
```glsl
// Black-body temperature to RGB
float t = temperature / 40000.0;
vec3 color = mix(
    vec3(1.0, 0.3, 0.0),      // 10K: red-orange
    vec3(1.0, 0.9, 0.6),      // 20K: white-yellow
    vec3(0.6, 0.8, 1.0), t);  // 40K: blue-white

// Size varies with radius
float size = mix(2.0, 6.0, 1.0 - radius / radius_max);

// Falloff from center
float falloff = smoothstep(0.5, 0.0, distance_from_center);

// Dual output
gl_FragData[0] = vec4(color, 1.0);
gl_FragData[1] = vec4(color * 5.0, 1.0);  // Bloom contribution
```

---

### 6.2 Rebirth Particle Pool (Generic System)

**Purpose:** Unified particle system for all rebirth phases (6-17)

**Architecture:**

```python
class ParticlePool:
    max_particles = 100,000
    particles = []  # List[Particle]
    
    def spawn_phase_particles(phase):
        pattern = PHASE_PATTERNS[phase]
        
        if pattern == "burst":
            spawn_radial_burst(origin, count)
        elif pattern == "sphere":
            spawn_sphere_shell(origin, count)
        elif pattern == "disk":
            spawn_disk_rotation(origin, count)
        
        # Each particle: position, velocity, lifetime, color, size
```

**Per-Phase Specification:**

| Phase | Pattern | Color | Duration |
|-------|---------|-------|----------|
| 6 (HAWKING) | Subtle glow | White-yellow | 12 sec |
| 7 (BIG_BANG) | Radial burst | Yellow-white | 3 sec |
| 8 (QUARK_PLASMA) | Expanding sphere | Blue-violet | 5 sec |
| 9 (PARTICLE_FORM) | Cooling collapse | Blue→Cyan | 5 sec |
| 10 (NUCLEOSYNTH) | Rotating disk | Yellow-orange | 4 sec |
| 11 (DARK_AGE) | Minimal | Dark blue | 5 sec |
| 12 (FIRST_STARS) | Star bursts | White points | 7 sec |
| 13 (GALAXY_FORM) | Spiral galaxy | White-cyan mix | 8 sec |
| 14 (NEBULA) | Cloud swirls | Rainbow colors | 6 sec |
| 15 (PROTOPLANETS) | Disk clumping | Gray-brown | 7 sec |
| 16 (NEW_WORLD) | Settling | Blue-green | 5 sec |

---

## 7. INTEGRATION METHODOLOGY

### 7.1 Main Loop Execution Order

```python
# main.py: Simulator.run()

dt = 0        # Time since last frame
while running:
    # ===== 1. INPUT HANDLING =====
    dt = clock.tick(60) / 1000.0  # Frame time in seconds
    glfw.poll_events()
    input_handler.process_keyboard()
    input_handler.process_mouse()
    imgui_io.process_input()
    
    # ===== 2. SCENE UPDATE (Physics) =====
    scene.update(dt)
        ├─ if state == NORMAL:
        │   └─ update_analytic_orbits(dt)
        ├─ elif state == APPROACH:
        │   └─ physics.step(dt × 1.5)
        ├─ elif state == SINGULARITY:
        │   └─ accretion_disk.update(dt)
        ├─ elif state == DEVOUR:
        │   └─ apply_tidal_forces_and_fade(dt)
        └─ elif HAWKING ≤ state ≤ NEW_WORLD:
            └─ particle_pool.update(dt)
    
    # ===== 3. CAMERA UPDATE =====
    camera.update(dt)
        ├─ compute_view_matrix()
        └─ compute_projection_matrix()
    
    # ===== 4. RENDER TO SCENE FBO =====
    hdr.bind_scene()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Render all objects
    render_stars(camera)
    render_grid(camera)
    render_planets(camera)
    render_blackhole(camera)
    render_accretion_disk(camera)
    
    hdr.unbind_scene()
    
    # ===== 5. POST-PROCESSING =====
    hdr.lensing_pass()      # Pass 1: Gravitational lensing
    hdr.bloom_pass()        # Pass 2: Bloom (8 iterations)
    hdr.composite_pass()    # Pass 3: Tone-map + composite
    
    # ===== 6. IMGUI OVERLAY =====
    imgui.new_frame()
    draw_hud_panels()
    imgui.render()
    
    # ===== 7. PRESENT =====
    glfw.swap_buffers()
```

**Frame Budget (60 FPS = 16.7 ms):**
- Physics: ~2-4 ms
- Rendering: ~8-10 ms
- Post-processing: ~2-3 ms
- ImGui: ~0.5-1 ms

---

### 7.2 Data Flow Diagram

```
User Input (KB/MS/ImGui)
    ↓
Scene.update(dt) [Determine phase-specific logic]
    ↓
Physics.step() [Compute N-body forces, integrate, detect collisions]
    ↓
Object State Updated [Positions, velocities, lifecycle]
    ↓
Camera.update() [Compute view/projection matrices]
    ↓
Render Loop:
    ├─ For each ShaderProgram:
    │   ├─ Bind VAO/VBO
    │   ├─ Set uniforms (MVP, light, etc.)
    │   └─ glDrawArrays()/glDrawElements()
    ├─ Write to MRT [Scene, Bright, ObjectID]
    ├─ Lensing pass [GPU post-proc]
    ├─ Bloom pass [GPU post-proc]
    └─ Composite pass [Tone-map to LDR]
    ↓
ImGui.render() [Overlay HUD]
    ↓
Display (swap buffers to screen)
```

---

## 8. PERFORMANCE CONSIDERATIONS

### 8.1 Optimization Strategies

| Component | Strategy | Rationale |
|-----------|----------|-----------|
| **N-Body** | O(N²) all-pairs (8 objects → negligible) | Accuracy > speed for small N |
| **Accretion Disk** | GPU particle streaming via VBO | 30K particles → CPU bottleneck without GPU |
| **Rendering** | Deferred + HDR for complex effects | Decouples object count from effect complexity |
| **Bloom** | Separable Gaussian (8×) | Separable kernel is O(w+h) vs O(w·h) |
| **Procedural Textures** | Generated once at startup | numpy FBM → cached in GPU texture memory |
| **Frustum Culling** | Minimal (all objects visible) | Scene is 360° view (space simulator) |

### 8.2 Scalability

**Can be extended to:**
- **Larger N-body:** Current O(N²) → use Barnes-Hut tree (O(N log N)) for 100+ objects
- **More Particles:** Accretion disk → particle streaming mesh (GPGPU compute)
- **Multiple Black Holes:** Expand scene manager to support multiple attractors
- **Relativistic Effects:** Current Newtonian → add Schwarzschild metric corrections

---

## 9. VALIDATION & VERIFICATION METHODOLOGY

### 9.1 Physics Correctness

**Test Cases:**
1. **Circular Orbits:** Verify Moon/ISS maintain period and altitude
2. **N-Body Stability:** Check energy conservation (E_kinetic + E_potential)
3. **Horbit Collision:** Verify detection triggers at correct distance threshold
4. **Black Hole Growth:** Verify Rs interpolates correctly from initial to final mass
5. **Accretion Dynamics:** Verify particles inspiral and respawn correctly

### 9.2 Rendering Correctness

**Test Cases:**
1. **HDR Preservation:** Verify 16F textures don't clip on bright pixels
2. **Bloom Accumulation:** Verify 8-pass blur produces smooth glow without banding
3. **Lensing Distortion:** Verify UV shift is proportional to distance from BH
4. **Tone-Mapping:** Verify Reinhard compresses highlights while preserving midtones
5. **Gamma Correction:** Verify sRGB display gamma applied correctly (1/2.2)

### 9.3 User Interaction

**Test Cases:**
1. **Camera Orbit:** Left drag rotates smoothly
2. **Mouse Picking:** Click selects expected object (object ID readback)
3. **Phase Transitions:** SPACE triggers correct state machine transitions
4. **Slider Responsiveness:** ImGui parameter changes reflect in real-time

---

## 10. SUMMARY

**Incursion-2 Methodology Employs:**

✅ **18-Phase State Machine** — Orchestrates universe lifecycle with deterministic timing  
✅ **Physics-Accurate Simulation** — Newtonian N-body + Schwarzschild metric  
✅ **Advanced Rendering Pipeline** — Deferred shading, HDR, bloom, gravitational lensing  
✅ **GPU-Accelerated Particles** — 30K accretion disk + rebirth effect system  
✅ **Modular Architecture** — 12 independent Python modules, clear separation of concerns  
✅ **Real-Time Interactivity** — Camera control, object picking, diagnostic HUD  
✅ **Production-Quality Graphics** — Tone-mapping, gamma correction, procedural textures  

**Perfect for:** Educational simulation, real-time graphics demos, astrophysics visualization

---

**Document Version:** 1.0  
**Created:** April 17, 2026  
**For:** Academic/University Project Presentation  
