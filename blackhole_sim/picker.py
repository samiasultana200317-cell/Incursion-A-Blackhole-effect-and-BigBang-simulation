from hdr import HDR

class Picker:
    def __init__(self):
        pass

    def pick(self, hdr, x, y):
        # Uses HDR.read_id
        return hdr.read_id(x, y)

class RayCaster:
    def ray_from_screen(self, x, y, view, proj, w, h):
        import numpy as np
        # NDC
        nx = 2.0 * x / w - 1.0
        ny = 1.0 - 2.0 * y / h
        
        # Clip
        clip = np.array([nx, ny, -1.0, 1.0], dtype=np.float32)
        
        # Eye
        invProj = np.linalg.inv(proj)
        eye = invProj @ clip
        eye[2] = -1.0
        eye[3] = 0.0
        
        # World
        invView = np.linalg.inv(view)
        world = invView @ eye
        ray = world[:3]
        return ray / np.linalg.norm(ray)

    def intersect_sphere(self, origin, ray, center, radius):
        import numpy as np
        oc = origin - center
        b = np.dot(ray, oc)
        c = np.dot(oc, oc) - radius * radius
        disc = b * b - c
        if disc < 0: return False, 0
        t = -b - np.sqrt(disc)
        return t > 0, t
