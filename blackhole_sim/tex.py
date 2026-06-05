import numpy as np
from OpenGL.GL import *
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def load_texture(path, wrap=GL_REPEAT):
    if HAS_PIL:
        try:
            img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
            data = np.array(img, dtype=np.uint8)
            w, h = img.size
            return create_gl_texture(data, w, h, wrap)
        except:
            pass
    return None

def create_gl_texture(data, w, h, wrap=GL_REPEAT, filter=GL_LINEAR):
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
    glGenerateMipmap(GL_TEXTURE_2D)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
    return tex

def fbm(w, h, octaves=6, scale=1.0):
    noise = np.zeros((h, w), dtype=np.float32)
    for i in range(octaves):
        freq = 2**i * scale
        amp = 0.5**i
        # Vectorized noise approximation using sine waves
        x = np.linspace(0, freq * 2 * np.pi, w)
        y = np.linspace(0, freq * 2 * np.pi, h)
        X, Y = np.meshgrid(x, y)
        noise += amp * (np.sin(X + np.sin(Y)) * 0.5 + 0.5)
    return noise / (2.0 - 0.5**(octaves-1))

def proc_earth_day(w, h):
    noise = fbm(w, h, 6, 2.0)
    data = np.zeros((h, w, 3), dtype=np.uint8)
    # Ocean
    mask_ocean = noise < 0.45
    data[mask_ocean] = [10, 30, 80]
    # Land
    mask_land = (noise >= 0.45) & (noise < 0.7)
    data[mask_land] = [30, 100, 30]
    # Mountains
    mask_mount = (noise >= 0.7) & (noise < 0.85)
    data[mask_mount] = [100, 80, 40]
    # Snow
    mask_snow = noise >= 0.85
    data[mask_snow] = [230, 230, 250]
    # Polar snow
    y_coords = np.linspace(-1, 1, h)
    polar_mask = (np.abs(y_coords[:, None]) > 0.85).repeat(w, axis=1)
    data[polar_mask] = [255, 255, 255]
    return create_gl_texture(data, w, h)

def proc_earth_night(w, h):
    data = np.zeros((h, w, 3), dtype=np.uint8)
    for _ in range(50):
        rx, ry = np.random.randint(0, w), np.random.randint(0, h)
        size = np.random.randint(5, 20)
        data[max(0, ry-size):min(h, ry+size), max(0, rx-size):min(w, rx+size)] = [255, 200, 100]
    return create_gl_texture(data, w, h)

def proc_clouds(w, h):
    noise = fbm(w, h, 5, 3.0)
    data = np.zeros((h, w, 3), dtype=np.uint8)
    mask = noise > 0.55
    val = ((noise[mask] - 0.55) * 255 / 0.45).astype(np.uint8)
    data[mask] = np.stack([val, val, val], axis=-1)
    return create_gl_texture(data, w, h)

def proc_moon(w, h):
    noise = fbm(w, h, 6, 4.0)
    val = (noise * 128 + 64).astype(np.uint8)
    data = np.stack([val, val, val], axis=-1)
    return create_gl_texture(data, w, h)

def proc_planet_rocky(w, h, hue=(150, 100, 50)):
    noise = fbm(w, h, 6, 2.0)
    data = (noise[..., None] * np.array(hue)).astype(np.uint8)
    return create_gl_texture(data, w, h)

def proc_planet_lava(w, h):
    noise = fbm(w, h, 6, 5.0)
    data = np.zeros((h, w, 3), dtype=np.uint8)
    # Dark rock
    data[:] = [40, 10, 5]
    # Lava cracks
    mask = noise > 0.7
    data[mask] = [255, 60, 0]
    return create_gl_texture(data, w, h)
