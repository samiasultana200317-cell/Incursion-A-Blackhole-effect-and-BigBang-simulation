import numpy as np

class Camera:
    def __init__(self):
        self.eye = np.array([0.0, 5.0, 10.0], dtype=np.float32)
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        
        self.yaw = -90.0
        self.pitch = -20.0
        self.dist = 12.0
        
        self.fov = 45.0
        self.mode = "ORBIT" # ORBIT, FOLLOW_BH, FOLLOW_EARTH, FOLLOW_ISS
        self.target_obj = None

    def update(self, dt, target_pos=None):
        if self.mode == "ORBIT":
            # Manual orbit update handled in main.py via mouse
            pass
        elif self.mode != "ORBIT" and target_pos is not None:
            # Smoothly lerp target
            self.target = self.target * 0.9 + target_pos * 0.1
            
        # Recompute eye based on orientation
        if self.mode == "ORBIT":
            pr = np.radians(self.pitch)
            yr = np.radians(self.yaw)
            self.eye[0] = self.target[0] + self.dist * np.cos(pr) * np.cos(yr)
            self.eye[1] = self.target[1] + self.dist * np.sin(pr)
            self.eye[2] = self.target[2] + self.dist * np.cos(pr) * np.sin(yr)
        else:
            # In follow mode, we keep a relative offset or just look at it
            # For this sim, let's keep the orbit distance but follow the target
            pr = np.radians(self.pitch)
            yr = np.radians(self.yaw)
            self.eye[0] = self.target[0] + self.dist * np.cos(pr) * np.cos(yr)
            self.eye[1] = self.target[1] + self.dist * np.sin(pr)
            self.eye[2] = self.target[2] + self.dist * np.cos(pr) * np.sin(yr)

    def process_mouse(self, dx, dy):
        self.yaw += dx * 0.2
        self.pitch = np.clip(self.pitch - dy * 0.2, -89, 89)

    def process_scroll(self, delta):
        self.dist = np.clip(self.dist - delta, 1.0, 100.0)
