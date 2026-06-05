BlackHole Simulator/
├── Core Rendering
│   ├── HDR Framebuffer (MRT: scene + bright)
│   ├── Gaussian Bloom (ping-pong, 8 pass)
│   ├── Gravitational Lensing Pass (screen-space UV distortion)
│   └── Reinhard Tone-map + Gamma composite
│
├── Scene Objects
│   ├── Earth (UV sphere, day/night shader, atmosphere)
│   ├── Moon (orbit, earthshine)
│   ├── ISS (procedural geometry, orbit)
│   ├── Space-Time Grid (deformable mesh, gravity warp)
│   ├── Demo Planets × 3 (collapse triggers)
│   └── Black Hole (accretion disk, lensing, event horizon)
│
├── Physics Simulation
│   ├── Gravitational N-body (simplified)
│   ├── Schwarzschild radius calculation
│   ├── Tidal spaghettification forces
│   └── Accretion disk particle system
│
├── Animation State Machine
│   ├── NORMAL → COLLAPSE → MERGE → SINGULARITY → DEVOUR
│   └── Per-object devour animation (stretch → shrink → gone)
│
└── HUD / Control Panel
    ├── Floating overlay (ImGui or custom quads)
    ├── All scene parameters (sliders, toggles)
    ├── "TRIGGER COLLAPSE" button
    └── Mouse picking (ray-cast click on objects)


    Phase 1 — NORMAL
  Earth orbits sun, Moon orbits Earth, ISS orbits Earth
  Space-time grid deforms with gravity: depth ∝ mass/distance²

Phase 2 — COLLAPSE (triggered by button)
  3 massive demo planets appear at distance ~8 units
  They accelerate toward each other via N-body gravity
  Grid deformation intensifies as they approach

Phase 3 — MERGE
  Planets reach critical separation → merger flash
  Combined mass M = M1 + M2 + M3
  Schwarzschild radius: Rs = 2GM/c²  (scaled for visuals)

Phase 4 — SINGULARITY
  Black hole forms at merge point
  Accretion disk spins up (particles orbit at Rs * 3)
  Gravitational lensing distortion begins on screen
  Space-time grid collapses inward

Phase 5 — DEVOUR
  Black hole grows, Rs expands
  Objects within Rs*influence get tidal force applied
  Spaghettification: stretch along radial axis, compress laterally
  Object fades + spirals inward → disappears at event horizon
  Order: demo planets → ISS → Moon → Earth







  ┌─────────────────────────────────────────────────┐
│  🌌 BLACK HOLE SIMULATOR          [RESET]        │
├─────────────────────────────────────────────────┤
│  SCENE                                          │
│  Sun angle    ████████░░  45°                   │
│  Earth spin   ████░░░░░░  ON  [toggle]          │
│  Moon speed   ██████░░░░  1.0×                  │
│  ISS speed    ████████░░  1.0×                  │
│  Grid density ██████░░░░  40                    │
│  Grid opacity ████████░░  0.6                   │
├─────────────────────────────────────────────────┤
│  CAMERA                                         │
│  [Orbit] [Follow BH] [Earth] [ISS]              │
│  FOV    ████████░░  45°                         │
│  Zoom   ████████░░  5.5                         │
├─────────────────────────────────────────────────┤
│  POST FX                                        │
│  Bloom  ████████░░  1.5                         │
│  Lens   ██████░░░░  1.0                         │
│  Exposure ████████  1.2                         │
├─────────────────────────────────────────────────┤
│  BLACK HOLE EVENT                               │
│  ┌─────────────────────────────────────────┐   │
│  │  ⚠  TRIGGER GRAVITATIONAL COLLAPSE  ⚠  │   │
│  └─────────────────────────────────────────┘   │
│  Mass scale  ██████░░░░  1.0×                   │
│  BH growth   ████████░░  1.0×                   │
│  Devour speed ████░░░░░░  1.0×                  │
├─────────────────────────────────────────────────┤
│  STATUS:  [ NORMAL ORBIT ]                      │
│  Phase: ░░░░░░░░░░░░░░░░░░░░  0%               │
└─────────────────────────────────────────────────┘







Build a complete, production-ready Python + OpenGL 3.3 Core Profile
"Black Hole Simulator". Every file must be fully implemented — no
placeholders, no TODO, no stub functions. Runs with: python main.py

═══════════════════════════════════════════════════════════════════
TECHNOLOGY STACK
═══════════════════════════════════════════════════════════════════

Python 3.10+
PyOpenGL 3.1.7+       pip install PyOpenGL PyOpenGL_accelerate
glfw 2.6+             pip install glfw
numpy 1.24+           pip install numpy
imgui[glfw] 2.0+      pip install imgui[glfw]
Pillow 10+            pip install Pillow  (optional, graceful fallback)

ALL shaders: #version 330 core
ALL geometry: VAO / VBO / EBO — no legacy GL
ALL math: numpy float32 — no GLM, no scipy

═══════════════════════════════════════════════════════════════════
PROJECT STRUCTURE
═══════════════════════════════════════════════════════════════════

blackhole_sim/
├── main.py           Window, render loop, orchestration, ImGui HUD
├── shader.py         GLSL compile + uniform setters (si sf sb sv3 sv4 sm4)
├── geo.py            All geometry builders + matrix helpers
├── tex.py            Texture loading + numpy procedural fallbacks
├── hdr.py            HDR FBO + MRT + bloom + lensing pipeline
├── physics.py        N-body, Schwarzschild, tidal, orbital
├── scene.py          All scene objects, state machine, devour logic
├── camera.py         Orbit / follow / locked modes + smooth lerp
├── particles.py      Accretion disk CPU particle system (numpy)
├── picker.py         Mouse ray-casting + object ID read-back
├── requirements.txt
├── README.md
├── textures/
└── shaders/
    ├── earth.vert   / earth.frag
    ├── atmo.vert    / atmo.frag
    ├── moon.vert    / moon.frag
    ├── iss.vert     / iss.frag     (reuse obj.vert/frag for metallic)
    ├── obj.vert     / obj.frag     (GGX PBR metallic, ISS + rocket)
    ├── grid.vert    / grid.frag    (space-time warp mesh)
    ├── planet.vert  / planet.frag  (demo collapse planets)
    ├── blackhole.vert / blackhole.frag
    ├── accretion.vert / accretion.frag
    ├── devour.vert  / devour.frag
    ├── stars.vert   / stars.frag
    ├── blur.vert    / blur.frag
    ├── lensing.frag               (gravitational UV distortion, fullscreen)
    └── composite.frag             (HDR + bloom + tone-map)

═══════════════════════════════════════════════════════════════════
HDR PIPELINE (hdr.py) — MANDATORY
═══════════════════════════════════════════════════════════════════

class HDR:
  scene_fbo — 3 GL_RGBA16F colour attachments:
    [0] scene colour
    [1] bright-pass (luminance threshold > 0.8)
    [2] object ID (float, for mouse picking)
  One GL_DEPTH24_STENCIL8 renderbuffer

  lens_fbo  — 1 GL_RGBA16F (scene after lensing distortion)
  ping_fbo[2] — Gaussian bloom ping-pong

  Methods:
    bind_scene()        → bind scene_fbo, clear, set glDrawBuffers(3)
    lensing_pass(lensing_sh, bh_screen_pos, rs_screen, strength)
        → read scene[0], write lensed to lens_fbo
    bloom_pass(blur_sh, iters=8)
        → ping-pong blur on bright attachment [1]
    composite(comp_sh, exposure, bloom_str)
        → combine lens_fbo + bloom → default framebuffer
    read_id(x, y) → int
        → glReadBuffer(GL_COLOR_ATTACHMENT2); glReadPixels 1×1 → objectID

Lensing shader (lensing.frag):
  uniform sampler2D uScene;
  uniform vec2  uBHScreen;   // black hole NDC position
  uniform float uRsScreen;   // Rs in screen pixels
  uniform float uStrength;
  
  vec2 toCenter = uBHScreen - texCoord;
  float dist = length(toCenter);
  float theta = uRsScreen / (dist * 800.0 + 0.001);
  vec2  deflect = normalize(toCenter) * theta * uStrength;
  vec3  lensed = texture(uScene, texCoord + deflect).rgb;
  // Einstein ring brightening near Rs
  float ring = smoothstep(uRsScreen*1.4, uRsScreen*1.5, dist*800.)
             - smoothstep(uRsScreen*1.5, uRsScreen*1.6, dist*800.);
  lensed += vec3(1.0,0.8,0.4) * ring * 4.0;
  oColor = vec4(lensed, 1.0);

Composite shader (composite.frag):
  hdr = texture(uScene, uv).rgb + texture(uBloom, uv).rgb * uBloomStr
  mapped = hdr / (hdr + 1.0)              // Reinhard
  result = pow(mapped, vec3(1.0/2.2))     // gamma
  oColor = vec4(result, 1.0)

═══════════════════════════════════════════════════════════════════
PHYSICS (physics.py)
═══════════════════════════════════════════════════════════════════

class NBody:
  positions  np.ndarray (N, 3) float64
  velocities np.ndarray (N, 3) float64
  masses     np.ndarray (N,)   float64
  G = 0.5    (visual scale)
  softening = 0.1
  
  def acceleration(self):
    # vectorised numpy N-body
    r = positions[:,None,:] - positions[None,:,:]  # (N,N,3)
    d2 = (r**2).sum(axis=2) + softening**2          # (N,N)
    d3 = d2 * np.sqrt(d2)                           # (N,N)
    a = (G * masses[None,:,None] * r / d3[:,:,None]).sum(axis=1)
    np.fill_diagonal(a[:,0], 0); ...  (zero self-interaction)
    return a
  
  def step(self, dt):
    # Velocity Verlet integration
    a0 = self.acceleration()
    self.positions += self.velocities*dt + 0.5*a0*dt*dt
    a1 = self.acceleration()
    self.velocities += 0.5*(a0+a1)*dt

class SchwarzschildBH:
  G_scaled = 0.5
  c_scaled  = 5.0
  
  def rs(self, mass):
    return 2.0 * self.G_scaled * mass / (self.c_scaled**2)
  
  def tidal_force(self, bh_mass, obj_pos, bh_pos, obj_radius):
    r = np.linalg.norm(obj_pos - bh_pos)
    return 2.0 * self.G_scaled * bh_mass * obj_radius / max(r**3, 0.001)
  
  def orbital_speed(self, bh_mass, radius):
    return np.sqrt(self.G_scaled * bh_mass / max(radius, 0.01))

class Orbits:
  # Analytic circular orbits for NORMAL phase (no N-body needed)
  def moon_pos(t, speed=1.):
    period=27.; a=t*speed*2*np.pi/period; tilt=np.radians(5.14); r=3.5
    return np.array([r*np.cos(a), r*np.sin(a)*np.sin(tilt),
                     r*np.sin(a)*np.cos(tilt)], np.float32)
  
  def iss_pos(t, speed=1.):
    period=10.; a=t*speed*2*np.pi/period; tilt=np.radians(51.6); r=1.38
    return np.array([r*np.cos(a), r*np.sin(a)*np.sin(tilt),
                     r*np.sin(a)*np.cos(tilt)], np.float32)

═══════════════════════════════════════════════════════════════════
PARTICLES — ACCRETION DISK (particles.py)
═══════════════════════════════════════════════════════════════════

class AccretionDisk:
  N = 30000  (30k particles, numpy array)
  
  Arrays (all np.float32):
    positions   (N, 3)
    velocities  (N, 3)
    radii       (N,)        distance from BH center
    phi         (N,)        orbital angle
    temperature (N,)        10000..40000 K → colour
    alpha       (N,)        opacity
  
  Initialise:
    radii = uniform(Rs*1.5, Rs*6.0)
    phi   = uniform(0, 2π)
    Y     = radii * uniform(-0.06, 0.06)  (disk thickness)
    temperature = 40000 / (radii / Rs)    (hotter near center)
    positions = [radii*cos(phi), Y, radii*sin(phi)]
  
  update(dt, bh_mass, Rs):
    # Keplerian advance
    omega = sqrt(G * bh_mass / radii**3)
    phi  += omega * dt
    # Inspiral (slow inward drift)
    radii -= 0.001 * dt * (Rs / radii)
    # Respawn particles that cross event horizon
    mask = radii < Rs * 1.2
    radii[mask] = uniform(Rs*4., Rs*6., mask.sum())
    phi[mask]   = uniform(0, 2π, mask.sum())
    # Recompute positions
    Y = stored_Y * (radii / initial_radii)  # compress as r shrinks
    positions[:,0] = radii * cos(phi)
    positions[:,1] = Y
    positions[:,2] = radii * sin(phi)
  
  Upload positions to VBO each frame:
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferSubData(GL_ARRAY_BUFFER, 0, positions.nbytes, positions)
  
  Accretion shader (accretion.frag):
    // temperature → colour via black-body approximation
    float t = temperature / 40000.0;
    vec3 col = mix(vec3(1.0,0.3,0.0), // 10000K orange-red
                   mix(vec3(1.0,0.9,0.6),  // 20000K white-yellow
                       vec3(0.6,0.8,1.0),  // 40000K blue-white
                       t), t);
    // soft point sprite
    vec2 c = gl_PointCoord - 0.5;
    float a = smoothstep(0.5, 0.0, length(c)) * particle_alpha;
    oColor  = vec4(col, a);
    oBright = vec4(col * a * 2.0, a);  // strong bloom
    gl_PointSize = mix(2.0, 6.0, 1.0 - r/rs_max);

═══════════════════════════════════════════════════════════════════
SCENE STATE MACHINE (scene.py)
═══════════════════════════════════════════════════════════════════

States: NORMAL=0, APPROACH=1, MERGE_FLASH=2,
        SINGULARITY=3, DEVOUR=4, RESET=5

class SimState:
  state = NORMAL
  phase_t = 0.      # time within current state
  bh_rs   = 0.      # current black hole Rs
  bh_rs_target = 0. # computed from merged mass
  bh_pos  = vec3(0)
  flash_alpha = 0.
  
  Per-object DevourState:
    { NORMAL, TIDAL, INFALLING, GONE }
    stretch_factor   = 1.0
    compress_factor  = 1.0
    alpha            = 1.0
    angular_drift    = 0.0  (spiral angle offset)

  Transitions:
    NORMAL → APPROACH:
      trigger_collapse() called
      Spawn 3 planets at triangle positions
      Init N-body with planet masses

    APPROACH → MERGE_FLASH:
      when any two planets within (r1+r2)*0.8
      merge_centroid = mass-weighted average of all 3 positions
      total_mass = sum of planet masses
      flash_alpha = 1.0

    MERGE_FLASH → SINGULARITY:
      after 1.5 seconds
      Remove planet objects
      bh_rs_target = SchwarzschildBH.rs(total_mass)
      Start accretion disk
      Camera lerps toward BH

    SINGULARITY → DEVOUR:
      after bh_rs >= bh_rs_target * 0.95 (BH fully grown)
      Begin checking object distances

    DEVOUR (continuous):
      For each object:
        dist = ||obj_pos - bh_pos||
        influence = bh_rs * 8.0
        if dist < influence and state == NORMAL: → TIDAL
        if dist < bh_rs*2.0 and state == TIDAL:  → INFALLING
        if state == TIDAL:
          tidal = tidal_force(bh_mass, obj_pos, bh_pos, obj_radius)
          obj.stretch  = 1.0 + tidal * phase_t * devour_speed
          obj.compress = 1.0 / sqrt(obj.stretch)
          obj.alpha    = 1.0
        if state == INFALLING:
          obj.alpha -= dt * 0.3 * devour_speed
          obj.angular_drift += dt * orbital_speed(dist) * 0.1
          Lerp obj_pos toward bh_pos at rate dt * 0.5 * devour_speed
        if obj.alpha <= 0.0: → GONE

    DEVOUR → RESET (when all objects GONE or user presses R):
      flash black → rebuild all objects → NORMAL

═══════════════════════════════════════════════════════════════════
SPACE-TIME GRID (grid.vert / grid.frag)
═══════════════════════════════════════════════════════════════════

Mesh: N×N vertices in XZ plane, Y=−2.2, range [−10, 10]
N = user-controlled 10..60 (rebuild VBO on change)
Vertex layout: [x, y, z] = 3 floats, draw GL_LINES

grid.vert:
  uniform vec3  uAttractors[8];   // positions of all masses
  uniform float uMasses[8];       // mass of each
  uniform int   uNAttractors;
  uniform float uGravityScale;

  void main() {
    vec3 pos = aPos;
    float totalDeform = 0.0;
    for(int i=0; i<uNAttractors; i++) {
      vec2 d = pos.xz - uAttractors[i].xz;
      float dist = sqrt(dot(d,d)) + 0.4;
      totalDeform += uGravityScale * uMasses[i] / (dist * dist);
    }
    pos.y -= totalDeform;
    vDeform = clamp(totalDeform / 5.0, 0.0, 1.0);
    gl_Position = uProj * uView * vec4(pos, 1.0);
  }

grid.frag:
  vec3 cool   = vec3(0.18, 0.55, 1.00);
  vec3 hot    = vec3(1.00, 0.55, 0.10);
  vec3 danger = vec3(1.00, 0.10, 0.05);  // near BH
  vec3 col    = mix(mix(cool, hot, vDeform), danger,
                    smoothstep(0.7, 1.0, vDeform));
  oColor  = vec4(col, uOpacity);
  oBright = vec4(col * max(vDeform - 0.4, 0.0), uOpacity);

When BH active: pass BH position as attractor with huge mass
  → grid lines dramatically curve and funnel toward BH

═══════════════════════════════════════════════════════════════════
BLACK HOLE SHADER (blackhole.vert / blackhole.frag)
═══════════════════════════════════════════════════════════════════

Geometry: UV sphere, radius=1.0 (scale by Rs in model matrix)
stacks=48, slices=48

blackhole.frag:
  in vec3 vFragPos, vNorm;
  uniform vec3  uBHPos;
  uniform float uRs;
  uniform float uTime;

  void main() {
    vec3 toCenter = vFragPos - uBHPos;
    float r = length(toCenter);
    float nr = r / uRs;  // normalized radius (1.0 = event horizon)

    // Event horizon: pure black
    oColor = vec4(0.0, 0.0, 0.0, 1.0);

    // Photon sphere ring (nr ≈ 1.5)
    float ring = smoothstep(1.42, 1.50, nr)
               - smoothstep(1.50, 1.58, nr);
    vec3 ringCol = vec3(1.0, 0.72, 0.28) * ring * 10.0;

    // Outer glow fading off
    float glow = max(0.0, 1.0 - (nr - 1.0) / 0.8) * (1.0 - ring);
    glow = pow(glow, 3.0) * 0.4;
    vec3 glowCol = vec3(0.6, 0.4, 1.0) * glow;

    oColor  = vec4(ringCol + glowCol, 1.0);
    oBright = vec4((ringCol + glowCol) * 2.0, 1.0);
  }

═══════════════════════════════════════════════════════════════════
DEVOUR SHADER (devour.vert / devour.frag)
═══════════════════════════════════════════════════════════════════

devour.vert:
  layout(location=0) in vec3 aPos;
  layout(location=1) in vec3 aNormal;
  uniform mat4  uModel, uView, uProj;
  uniform vec3  uBHPos;
  uniform float uStretch;
  uniform float uCompress;
  uniform float uAlpha;
  uniform float uAngleDrift;

  void main() {
    // Spaghettification
    vec3 worldPos = vec3(uModel * vec4(aPos, 1.0));
    vec3 toBH     = normalize(uBHPos - worldPos);
    vec3 radial   = dot(aPos, toBH) * toBH;
    vec3 lateral  = aPos - radial;
    vec3 deformed = radial * uStretch + lateral * uCompress;
    // Spiral drift: rotate around BH
    float ca = cos(uAngleDrift); float sa = sin(uAngleDrift);
    vec3 spiraled = vec3(deformed.x*ca - deformed.z*sa,
                         deformed.y,
                         deformed.x*sa + deformed.z*ca);
    vAlpha  = uAlpha;
    vNormal = mat3(transpose(inverse(uModel))) * aNormal;
    gl_Position = uProj * uView * uModel * vec4(spiraled, 1.0);
  }

devour.frag:
  // Normal shading
  vec3 result = (ambient + diffuse) * baseColor + specular;
  // Heat glow near death
  float heat  = (1.0 - vAlpha) * 3.0;
  result     += vec3(1.0, 0.5, 0.1) * heat;
  oColor  = vec4(result, vAlpha);
  oBright = vec4(result * heat, vAlpha);

═══════════════════════════════════════════════════════════════════
MOUSE INTERACTION (picker.py)
═══════════════════════════════════════════════════════════════════

class Picker:
  def pick(hdr_fbo, x, y, window_height):
    # Read object ID from attachment [2]
    glBindFramebuffer(GL_READ_FRAMEBUFFER, hdr_fbo)
    glReadBuffer(GL_COLOR_ATTACHMENT2)
    pixel = glReadPixels(x, window_height-y, 1, 1,
                         GL_RGBA, GL_FLOAT)
    # R channel = object ID (0=none,1=Earth,2=Moon,3=ISS,4-6=planets,7=BH)
    obj_id = int(pixel[0][0][0] * 10 + 0.5)
    return obj_id

Each object shader writes its ID:
  layout(location=2) out vec4 oID;
  oID = vec4(float(uObjectID) / 10.0, 0, 0, 1);
  // uObjectID: 1=Earth,2=Moon,3=ISS,4-6=DemoPlanets,7=BH

On click → picked ID → highlight selected object (outline pass)
         → show object info panel in ImGui

class RayCaster (alternative for rough picking):
  def ray_from_screen(x, y, view, proj, w, h):
    ndc = vec2(2*x/w-1, 1-2*y/h)
    clip = vec4(ndc, -1, 1)
    eye  = inv(proj) * clip;  eye.z=-1; eye.w=0
    world = inv(view) * eye
    return normalize(world.xyz)
  
  def intersect_sphere(ray_origin, ray_dir, center, radius):
    oc = ray_origin - center
    b  = dot(ray_dir, oc)
    c  = dot(oc,oc) - radius*radius
    disc = b*b - c
    return disc >= 0  (and t = -b - sqrt(disc) > 0)

═══════════════════════════════════════════════════════════════════
IMGUI HUD PANEL (in main.py)
═══════════════════════════════════════════════════════════════════

Position: (12, 12), size: (320, 680), no resize, no collapse
Style: custom dark + blue accent
  imgui.push_style_color(COLOR_HEADER,       0.15, 0.35, 0.65, 1)
  imgui.push_style_color(COLOR_BUTTON,       0.20, 0.45, 0.80, 1)
  imgui.push_style_color(COLOR_FRAME_BG,     0.10, 0.10, 0.15, 1)
  imgui.push_style_color(COLOR_WINDOW_BG,    0.05, 0.05, 0.10, 0.92)

Sections (tree_node collapsible):

"SCENE CONTROLS"
  sun_angle     slider_float  0..360
  sun_elev      slider_float  -30..80
  sun_intensity slider_float  0..1
  auto_spin     checkbox + spin_speed slider_float
  moon_speed    slider_float  0.1..8
  iss_speed     slider_float  0.1..8
  grid_density  slider_int    10..60
  grid_opacity  slider_float  0..1
  show_atmo     checkbox
  show_rings    checkbox

"CAMERA"
  radio_button for each mode: Orbit / Follow BH / Earth / ISS
  cam_fov       slider_float  20..120
  reset camera  button

"POST PROCESSING"
  bloom_str     slider_float  0..4
  lens_strength slider_float  0..3  (0 = no lensing)
  exposure      slider_float  0.1..4

"BLACK HOLE EVENT" (red accent border push_style_color)
  bh_mass_mult  slider_float  0.1..5
  bh_growth_spd slider_float  0.1..5
  devour_speed  slider_float  0.1..5
  disk_density  slider_float  0..1

  Big button with red color:
    if state == NORMAL:
      if button("  ⚠  TRIGGER GRAVITATIONAL COLLAPSE  ⚠", 294, 40):
        scene.trigger_collapse()
    elif state == DEVOUR or all GONE:
      if button("  RESET SIMULATION  ", 294, 40):
        scene.reset()
    else:
      text_disabled("  Mission in progress...")

"STATUS"
  text with color:
    NORMAL    → green
    APPROACH  → yellow
    MERGE_FLASH → white flash (bright)
    SINGULARITY → purple
    DEVOUR    → red
    RESET     → grey
  progress_bar(phase_t / phase_duration)
  For each object: text colored by devour state

"SELECTED OBJECT INFO" (shows on click)
  Object name, position, distance to BH, status

═══════════════════════════════════════════════════════════════════
RENDER ORDER EVERY FRAME
═══════════════════════════════════════════════════════════════════

hdr.bind_scene()                 ← MRT FBO, 3 attachments
  depth_mask ON
  Stars       (depth OFF, additive)
  Moon        (opaque)
  Earth       (opaque)
  Atmosphere  (blend, cull_front, depth OFF)
  ISS         (opaque, all sub-parts)
  Demo planets (opaque, if state >= APPROACH)
  Space-time grid (blend, lines, depth OFF during devour)
  Black hole  (opaque, if state >= SINGULARITY)
  Accretion disk (point sprites, additive blend, depth OFF)
  All objects in TIDAL/INFALLING state: re-draw with devour shader
  Orbit rings (line strips, blend, depth OFF)

hdr.lensing_pass(...)            ← if BH active
hdr.bloom_pass(blur_sh, 8)       ← bright attachment [1]
hdr.composite(comp_sh, exposure, bloom_str)

ImGui render                     ← default framebuffer, on top

═══════════════════════════════════════════════════════════════════
KEYBOARD + MOUSE
═══════════════════════════════════════════════════════════════════

Mouse:
  Left drag   Orbit (ORBIT mode)
  Scroll      Zoom
  Left click  Pick object → show info, highlight
  Double-click Follow that object

Keys:
  SPACE  Trigger collapse / Reset
  C      Cycle camera modes
  R      Reset simulation
  G      Toggle grid
  A      Toggle atmosphere
  N      Flip sun
  B      Toggle bloom
  ESC/Q  Quit

═══════════════════════════════════════════════════════════════════
GEO.PY — GEOMETRY + MATRIX HELPERS
═══════════════════════════════════════════════════════════════════

Functions:
  build_sphere(r, stacks, slices)   → (vao,n)  [xyz nxyz uv tan] 11f
  build_sphere_simple(r,s,s)        → (vao,n)  [xyz nxyz uv]     8f
  build_cylinder(r,h,segs,caps)     → (vao,n)  [xyz nxyz]        6f
  build_cone(r,h,segs)              → (vao,n)  [xyz nxyz]        6f
  build_box(w,h,d)                  → (vao,n)  [xyz nxyz]        6f
  build_grid(N, size)               → (vao, line_count)  [xyz]   3f
  build_stars(n,seed)               → (vao,n)  [xyz br]          4f
  build_ring(r,segs,tilt,axis)      → (vao,n)  line strip        3f
  build_disk_particles(N)           → (vao, vbo, N)  dynamic VBO

Matrix helpers (numpy float32 4×4):
  I() T(x,y,z) S(x,y,z) Rx(a) Ry(a) Rz(a)
  look_at(eye,ctr,up)
  perspective(fov_deg, aspect, near=0.01, far=800.)
  project_to_screen(world_pos, view, proj, w, h) → (sx, sy, depth)

═══════════════════════════════════════════════════════════════════
TEX.PY — PROCEDURAL TEXTURES
═══════════════════════════════════════════════════════════════════

All generators fully vectorised numpy — zero Python pixel loops.
Each returns np.uint8 array (H, W, 3):

  proc_earth_day(1024, 512)    6-oct fBm, 6 biomes, polar snow
  proc_earth_night(1024, 512)  city clusters at real positions
  proc_earth_normal(512, 256)  flat (128,128,255) normal map
  proc_earth_spec(512, 256)    ocean=200, land=30 per fBm
  proc_clouds(1024, 512)       fBm threshold 0.42
  proc_moon(512, 256)          grey fBm + crater ring overlay
  proc_planet_rocky(512,256,hue) rocky planet with tint colour
  proc_planet_icy(512,256)     blue-white icy surface
  proc_planet_lava(512,256)    dark red with bright cracks

═══════════════════════════════════════════════════════════════════
CRITICAL IMPLEMENTATION RULES
═══════════════════════════════════════════════════════════════════

1. EVERY scene shader outputs 3 attachments:
   layout(location=0) out vec4 oColor;
   layout(location=1) out vec4 oBright;
   layout(location=2) out vec4 oID;

2. Gravitational lensing is a SEPARATE fullscreen post-process pass —
   not faked inside the scene shader.

3. Spaghettification = non-uniform scale built in devour.vert using
   tidal force magnitude, NOT a texture or colour effect.

4. Black hole event horizon is a pure black sphere with photon sphere
   ring computed analytically in blackhole.frag. No texture.

5. Accretion disk: 30,000 point sprite particles. VBO updated every
   frame via glBufferSubData. Keplerian advance in numpy each tick.

6. N-body uses Velocity Verlet. No Euler.

7. Mouse picking via glReadPixels from attachment [2] on click only.

8. Camera always smooth-lerps. No instant position jumps.

9. All procedural textures are numpy-vectorised.

10. imgui, Pillow: graceful fallback if not installed.

11. Runs: python main.py — zero arguments, zero config files needed.

12. HDR FBO is mandatory. Direct render to default framebuffer
    is never acceptable for any scene content.

13. Space-time grid vertex displacement is computed IN THE VERTEX
    SHADER via uniforms — not on the CPU.

14. Devour order strictly: demo planets first → ISS → Moon → Earth.
    Each must complete (alpha=0) before the next begins TIDAL state.