# Black Hole Simulator

A production-ready Python + OpenGL 3.3 Core Profile simulator featuring HDR, bloom, gravitational lensing, and spaghettification physics.

## Features
- **HDR Pipeline**: Multi-render target FBO with 16-bit float textures.
- **Gravitational Lensing**: Real-time post-process distortion pass.
- **Accretion Disk**: 30,000 particle CPU-simulated system with Keplerian orbits.
- **Spaghettification**: Geometric deformation based on tidal force in vertex shaders.
- **Physics**: N-body simulator with Velocity Verlet integration.
- **Procedural Textures**: Fully vectorized numpy Earth, Moon, and planet generation.
- **ImGui HUD**: Real-time controls for scene, camera, and post-processing.

## Installation
```bash
pip install -r requirements.txt
```

## Running
```bash
python main.py
```

## Controls
- **Mouse Left Drag**: Rotate camera (ORBIT mode).
- **Mouse Scroll**: Zoom in/out.
- **Mouse Left Click**: Select object to see info.
- **SPACE**: Trigger Gravitational Collapse.
- **R**: Reset Simulation.
- **C**: Cycle Camera Modes.
- **ESC/Q**: Quit.
