import numpy as np

def I(): return np.identity(4, dtype=np.float32)

def T(x, y, z):
    m = np.identity(4, dtype=np.float32)
    m[:3, 3] = [x, y, z]
    return m

def S(x, y, z):
    return np.diag([x, y, z, 1.0]).astype(np.float32)

def Rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=np.float32)

def Ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], dtype=np.float32)

def Rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float32)

def perspective(fov, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fov) / 2.0)
    return np.array([
        [f/aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
        [0, 0, -1, 0]
    ], dtype=np.float32)

def look_at(eye, target, up):
    f = target - eye
    f /= np.linalg.norm(f)
    s = np.cross(f, up)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.identity(4, dtype=np.float32)
    m[0, :3] = s
    m[1, :3] = u
    m[2, :3] = -f
    return m @ T(-eye[0], -eye[1], -eye[2])

def build_sphere(radius, stacks, slices):
    from OpenGL.GL import glGenVertexArrays, glGenBuffers, glBindVertexArray, glBindBuffer, \
                          glBufferData, glEnableVertexAttribArray, glVertexAttribPointer, \
                          GL_VERTEX_ARRAY, GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT, \
                          GL_ELEMENT_ARRAY_BUFFER, GL_TRIANGLES, glDrawElements
    
    verts = []
    for i in range(stacks + 1):
        phi = np.pi * i / stacks
        for j in range(slices + 1):
            theta = 2 * np.pi * j / slices
            x = np.sin(phi) * np.cos(theta)
            y = np.cos(phi)
            z = np.sin(phi) * np.sin(theta)
            u = j / slices
            v = i / stacks
            
            # Pos, Normal, UV, Tan (basic tan)
            verts.extend([x * radius, y * radius, z * radius]) # Pos
            verts.extend([x, y, z]) # Normal
            verts.extend([u, v]) # UV
            # Tangent (approximate)
            verts.extend([-np.sin(theta), 0, np.cos(theta)])
            
    indices = []
    for i in range(stacks):
        for j in range(slices):
            p1 = i * (slices + 1) + j
            p2 = p1 + (slices + 1)
            indices.extend([p1, p2, p1 + 1])
            indices.extend([p1 + 1, p2, p2 + 1])
            
    v_data = np.array(verts, dtype=np.float32)
    i_data = np.array(indices, dtype=np.uint32)
    
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)
    
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, v_data.nbytes, v_data, GL_STATIC_DRAW)
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, i_data.nbytes, i_data, GL_STATIC_DRAW)
    
    stride = 11 * 4
    # Pos
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, False, stride, None)
    # Normal
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, False, stride, ctypes.c_void_p(3 * 4))
    # UV
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, False, stride, ctypes.c_void_p(6 * 4))
    # Tan
    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 3, GL_FLOAT, False, stride, ctypes.c_void_p(8 * 4))
    
    glBindVertexArray(0)
    return vao, len(indices)

def build_grid(N, size, subs=80):
    from OpenGL.GL import glGenVertexArrays, glGenBuffers, glBindVertexArray, glBindBuffer, \
                          glBufferData, glEnableVertexAttribArray, glVertexAttribPointer, \
                          GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT
    
    verts = []
    step = size / (N - 1)
    start = -size / 2.0
    
    # Lines along Z direction (for each X position)
    for i in range(N):
        x = start + i * step
        for j in range(subs):
            z0 = start + size * j / subs
            z1 = start + size * (j + 1) / subs
            verts.extend([x, 0, z0])
            verts.extend([x, 0, z1])
    
    # Lines along X direction (for each Z position)
    for i in range(N):
        z = start + i * step
        for j in range(subs):
            x0 = start + size * j / subs
            x1 = start + size * (j + 1) / subs
            verts.extend([x0, 0, z])
            verts.extend([x1, 0, z])
        
    v_data = np.array(verts, dtype=np.float32)
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, v_data.nbytes, v_data, GL_STATIC_DRAW)
    
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
    
    glBindVertexArray(0)
    return vao, len(verts) // 3

def build_stars(n, seed=42):
    from OpenGL.GL import glGenVertexArrays, glGenBuffers, glBindVertexArray, glBindBuffer, \
                          glBufferData, glEnableVertexAttribArray, glVertexAttribPointer, \
                          GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT
    np.random.seed(seed)
    pos = np.random.uniform(-400, 400, (n, 3)).astype(np.float32)
    # Filter out stars too close to center
    mag = np.linalg.norm(pos, axis=1)
    pos = pos[mag > 100]
    n = len(pos)
    brightness = np.random.uniform(0.2, 1.0, (n, 1)).astype(np.float32)
    data = np.hstack([pos, brightness])
    
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
    
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 16, None)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 1, GL_FLOAT, False, 16, ctypes.c_void_p(12))
    
    glBindVertexArray(0)
    return vao, n

def build_ring(r, segs):
    from OpenGL.GL import glGenVertexArrays, glGenBuffers, glBindVertexArray, glBindBuffer, \
                          glBufferData, glEnableVertexAttribArray, glVertexAttribPointer, \
                          GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT
    verts = []
    for i in range(segs + 1):
        a = 2.0 * np.pi * i / segs
        verts.extend([r * np.cos(a), 0, r * np.sin(a)])
        
    v_data = np.array(verts, dtype=np.float32)
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, v_data.nbytes, v_data, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
    glBindVertexArray(0)
    return vao, segs + 1

def project_to_screen(pos, view, proj, w, h):
    p = proj @ view @ np.array([*pos, 1.0], dtype=np.float32)
    if p[3] == 0: return [0.5, 0.5, 0.0]
    ndc = p[:3] / p[3]
    screen = (ndc + 1.0) / 2.0
    return [screen[0]*w, (1.0-screen[1])*h, screen[2]]

import ctypes
