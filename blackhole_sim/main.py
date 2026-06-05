import glfw
from OpenGL.GL import *
import numpy as np
import imgui
from imgui.integrations.glfw import GlfwRenderer
import math, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from shader import Shader
from geo import I, T, Ry, S, Rx, perspective, look_at, build_sphere
from hdr import HDR
from camera import Camera
from picker import Picker
from scene import (Scene, NORMAL, APPROACH, MERGE_FLASH, SINGULARITY, DEVOUR, RESET,
                    HAWKING, BIG_BANG, QUARK_PLASMA, PARTICLE_FORM, NUCLEOSYNTH,
                    DARK_AGE, FIRST_STARS, GALAXY_FORM, NEBULA, PROTOPLANETS,
                    NEW_WORLD, IDLE_NEW, STATE_NAMES, STATE_COLORS, PHASE_FACTS, PHASE_DURATIONS)

class Simulator:
    def __init__(self):
        if not glfw.init(): sys.exit(1)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.width, self.height = 1280, 720
        self.window = glfw.create_window(self.width, self.height, "Black Hole Simulator", None, None)
        if not self.window: glfw.terminate(); sys.exit(1)
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)

        imgui.create_context()
        self.impl = GlfwRenderer(self.window)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_PROGRAM_POINT_SIZE)

        # Shaders
        self.sh_obj = Shader("shaders/obj.vert", "shaders/obj.frag")
        self.sh_devour = Shader("shaders/devour.vert", "shaders/devour.frag")
        self.sh_grid = Shader("shaders/grid.vert", "shaders/grid.frag")
        self.sh_stars = Shader("shaders/stars.vert", "shaders/stars.frag")
        self.sh_earth = Shader("shaders/obj.vert", "shaders/earth.frag")
        self.sh_moon = Shader("shaders/obj.vert", "shaders/moon.frag")
        self.sh_atmo = Shader("shaders/atmo.vert", "shaders/atmo.frag")
        self.sh_bh = Shader("shaders/blackhole.vert", "shaders/blackhole.frag")
        self.sh_accretion = Shader("shaders/accretion.vert", "shaders/accretion.frag")
        self.sh_blur = Shader("shaders/blur.vert", "shaders/blur.frag")
        self.sh_lensing = Shader("shaders/blur.vert", "shaders/lensing.frag")
        self.sh_composite = Shader("shaders/blur.vert", "shaders/composite.frag")
        # Rebirth shaders
        self.sh_plasma = Shader("shaders/blur.vert", "shaders/plasma.frag")
        self.sh_rebirth = Shader("shaders/rebirth.vert", "shaders/rebirth.frag")
        self.sh_bang = Shader("shaders/bang.vert", "shaders/bang.frag")

        self.hdr = HDR(self.width, self.height)
        self.camera = Camera()
        self.picker = Picker()
        self.scene = Scene()

        # Sphere VAO for bang/stars rendering
        self.sphere_vao, self.sphere_count = build_sphere(1.0, 32, 32)

        self.last_time = glfw.get_time()
        self.selected_id = 0

        self.sun_angle = 45.0; self.sun_elev = 20.0; self.sun_intensity = 1.0
        self.bloom_str = 1.5; self.lens_strength = 1.0; self.exposure = 1.0
        self.auto_spin = True; self.grid_height = -2.0
        self.gravity_scale = 0.5; self.show_orbits = True

        self.last_mouse_pos = [0, 0]; self.is_dragging = False

        glfw.set_scroll_callback(self.window, self.on_scroll)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_window_size_callback(self.window, self.on_resize)

    def on_resize(self, window, w, h):
        if w < 1 or h < 1: return
        self.width, self.height = w, h
        self.hdr.resize(w, h)
        glViewport(0, 0, w, h)

    def on_key(self, window, key, scancode, action, mods):
        if action != glfw.PRESS: return
        if key == glfw.KEY_SPACE:
            if self.scene.state == NORMAL: self.scene.trigger_collapse()
            elif self.scene.state >= NEW_WORLD: self.scene.reset()
        if key == glfw.KEY_R: self.scene.reset()
        if key == glfw.KEY_N: self.scene.skip_phase()
        if key == glfw.KEY_C:
            modes = ["ORBIT","FOLLOW_EARTH","FOLLOW_BH"]
            idx = (modes.index(self.camera.mode)+1)%len(modes)
            self.camera.mode = modes[idx]
        if key == glfw.KEY_ESCAPE: glfw.set_window_should_close(self.window, True)

    def on_scroll(self, w, xoff, yoff):
        if imgui.get_io().want_capture_mouse: return
        self.camera.process_scroll(yoff)

    def on_mouse_button(self, w, button, action, mods):
        if imgui.get_io().want_capture_mouse: return
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            x, y = glfw.get_cursor_pos(self.window)
            self.selected_id = self.picker.pick(self.hdr, int(x), int(y))

    # ─── HUD ───
    def render_ui(self):
        imgui.new_frame()
        imgui.set_next_window_position(12, 12, imgui.ONCE)
        imgui.set_next_window_size(360, 850, imgui.ONCE)
        imgui.begin("Simulator Controls", True, imgui.WINDOW_NO_COLLAPSE)

        st = self.scene.state
        if st < len(STATE_NAMES):
            col = STATE_COLORS[st]
            imgui.text_colored(STATE_NAMES[st], *col)
        if st < len(PHASE_FACTS) and PHASE_FACTS[st]:
            imgui.text_wrapped(PHASE_FACTS[st])
        # Phase progress
        if HAWKING <= st <= NEW_WORLD and PHASE_DURATIONS[st] > 0:
            dur = PHASE_DURATIONS[st] / self.scene.rebirth_speed
            imgui.progress_bar(min(self.scene.phase_t / dur, 1.0), (320, 14))

        imgui.spacing(); imgui.separator(); imgui.spacing()

        if imgui.tree_node("GRID & ENVIRONMENT", imgui.TREE_NODE_DEFAULT_OPEN):
            _, self.gravity_scale = imgui.slider_float("Gravity Scale", self.gravity_scale, 0, 5)
            _, self.grid_height = imgui.slider_float("Grid Height", self.grid_height, -10, 5)
            _, self.scene.grid_opacity = imgui.slider_float("Grid Opacity", self.scene.grid_opacity, 0, 1)
            _, self.show_orbits = imgui.checkbox("Show Orbits", self.show_orbits)
            imgui.separator()
            _, self.sun_angle = imgui.slider_float("Sun Angle", self.sun_angle, 0, 360)
            _, self.sun_elev = imgui.slider_float("Sun Elev", self.sun_elev, -30, 80)
            _, self.sun_intensity = imgui.slider_float("Sun Intensity", self.sun_intensity, 0, 5)
            _, self.auto_spin = imgui.checkbox("Auto Spin", self.auto_spin)
            imgui.tree_pop()

        if imgui.tree_node("CAMERA", imgui.TREE_NODE_DEFAULT_OPEN):
            if imgui.radio_button("Orbit", self.camera.mode=="ORBIT"): self.camera.mode="ORBIT"
            if imgui.radio_button("Follow Earth", self.camera.mode=="FOLLOW_EARTH"): self.camera.mode="FOLLOW_EARTH"
            if imgui.radio_button("Follow BH", self.camera.mode=="FOLLOW_BH"): self.camera.mode="FOLLOW_BH"
            _, self.camera.fov = imgui.slider_float("FOV", self.camera.fov, 20, 120)
            imgui.tree_pop()

        if imgui.tree_node("POST PROCESSING", imgui.TREE_NODE_DEFAULT_OPEN):
            _, self.lens_strength = imgui.slider_float("Lens Strength", self.lens_strength, 0, 5)
            _, self.exposure = imgui.slider_float("Exposure", self.exposure, 0.1, 5)
            _, self.bloom_str = imgui.slider_float("Bloom", self.bloom_str, 0, 3)
            _, self.scene.devour_speed = imgui.slider_float("Devour Speed", self.scene.devour_speed, 0.1, 5)
            imgui.tree_pop()

        if imgui.tree_node("UNIVERSE REBIRTH"):
            _, self.scene.rebirth_speed = imgui.slider_float("Rebirth Speed", self.scene.rebirth_speed, 0.5, 3.0)
            if imgui.button("Skip Phase", 140, 28): self.scene.skip_phase()
            imgui.same_line()
            if imgui.button("Reset All", 140, 28): self.scene.reset()
            if st == HAWKING:
                imgui.text(f"BH Mass: {self.scene.bh_mass:.3f}")
                imgui.text(f"BH Temp: {'%.0e' % (1e12 * max(self.scene.bh_temp, 0.01))} K")
            imgui.tree_pop()

        imgui.spacing(); imgui.separator(); imgui.spacing()
        if st == NORMAL:
            if imgui.button("TRIGGER COLLAPSE", 294, 40):
                self.scene.trigger_collapse()
        elif st >= NEW_WORLD:
            if imgui.button("RESET SIMULATION", 294, 40):
                self.scene.reset()
        else:
            imgui.text_disabled("  Simulation in progress...")

        imgui.end()
        imgui.render()
        self.impl.render(imgui.get_draw_data())

    # ─── MAIN LOOP ───
    def run(self):
        while not glfw.window_should_close(self.window):
            t = glfw.get_time()
            dt = min(t - self.last_time, 0.05)
            self.last_time = t

            glfw.poll_events()
            self.impl.process_inputs()

            if not imgui.get_io().want_capture_mouse:
                cm = glfw.get_cursor_pos(self.window)
                if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
                    if not self.is_dragging: self.is_dragging = True
                    else: self.camera.process_mouse(cm[0]-self.last_mouse_pos[0], cm[1]-self.last_mouse_pos[1])
                else: self.is_dragging = False
                self.last_mouse_pos = cm

            self.scene.update(dt)
            if self.auto_spin: self.sun_angle += dt * 10

            target_pos = None
            if self.camera.mode == "FOLLOW_EARTH" and len(self.scene.objects) > 0:
                target_pos = self.scene.objects[0].pos
            elif self.camera.mode == "FOLLOW_BH":
                target_pos = self.scene.bh_pos
            self.camera.update(dt, target_pos)

            view = look_at(self.camera.eye, self.camera.target, self.camera.up)
            proj = perspective(self.camera.fov, self.width / max(self.height, 1), 0.1, 1000)

            sr = np.radians(self.sun_angle); se = np.radians(self.sun_elev)
            sun_dir = np.array([np.cos(se)*np.cos(sr), np.sin(se), np.cos(se)*np.sin(sr)], dtype=np.float32)
            sun_col = np.array([1,1,1], dtype=np.float32) * self.sun_intensity

            # ─── RENDER ───
            self.hdr.bind_scene()
            glClearColor(0.01, 0.01, 0.02, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            st = self.scene.state

            # Stars (always, unless hidden by plasma)
            if st not in (QUARK_PLASMA, PARTICLE_FORM):
                stars_alpha = 1.0
                if st == NEW_WORLD:
                    stars_alpha = self.scene.new_world_alpha
                glDisable(GL_DEPTH_TEST)
                glPointSize(1.5)
                self.sh_stars.use()
                self.sh_stars.sm4("uView", view)
                self.sh_stars.sm4("uProj", proj)
                glBindVertexArray(self.scene.stars_vao)
                glDrawArrays(GL_POINTS, 0, self.scene.stars_count)
                glEnable(GL_DEPTH_TEST)

            # ─── NORMAL / APPROACH / DEVOUR objects ───
            if st <= DEVOUR or st == NEW_WORLD:
                obj_alpha = 1.0 if st != NEW_WORLD else self.scene.new_world_alpha
                for obj in self.scene.objects + self.scene.planets:
                    if obj.state == "GONE": continue
                    sh = self.sh_obj
                    if obj.state != "NORMAL": sh = self.sh_devour
                    elif obj.name == "Earth": sh = self.sh_earth
                    elif obj.name == "Moon": sh = self.sh_moon

                    sh.use()
                    sh.sm4("uView", view); sh.sm4("uProj", proj)
                    sh.sm4("uModel", T(*obj.pos) @ S(obj.scale, obj.scale, obj.scale))
                    sh.sv3("uSunDir", *sun_dir); sh.sv3("uSunCol", *sun_col)
                    sh.si("uObjectID", obj.id)

                    if obj.state != "NORMAL":
                        sh.sv3("uBHPos", *self.scene.bh_pos)
                        sh.sf("uStretch", obj.stretch); sh.sf("uCompress", obj.compress)
                        sh.sf("uAlpha", obj.alpha); sh.sf("uAngleDrift", obj.angular_drift)
                    else:
                        glActiveTexture(GL_TEXTURE0)
                        glBindTexture(GL_TEXTURE_2D, obj.texture)
                        sh.si("uTex", 0)

                    glBindVertexArray(obj.vao)
                    glDrawElements(GL_TRIANGLES, obj.count, GL_UNSIGNED_INT, None)

                    if obj.name == "Earth" and obj.state == "NORMAL":
                        glEnable(GL_BLEND); glDepthMask(GL_FALSE)
                        self.sh_atmo.use()
                        self.sh_atmo.sm4("uView", view); self.sh_atmo.sm4("uProj", proj)
                        self.sh_atmo.sm4("uModel", T(*obj.pos) @ S(obj.scale*1.025, obj.scale*1.025, obj.scale*1.025))
                        self.sh_atmo.sv3("uSunDir", *sun_dir); self.sh_atmo.sv3("uEarthPos", *obj.pos)
                        glBindVertexArray(obj.vao)
                        glDrawElements(GL_TRIANGLES, obj.count, GL_UNSIGNED_INT, None)
                        glDepthMask(GL_TRUE)

            # ─── BH + Accretion ───
            if SINGULARITY <= st <= HAWKING and self.scene.bh_rs > 0.01:
                self.sh_bh.use()
                self.sh_bh.sm4("uView", view); self.sh_bh.sm4("uProj", proj)
                rs = self.scene.bh_rs
                self.sh_bh.sm4("uModel", T(*self.scene.bh_pos) @ S(rs, rs, rs))
                self.sh_bh.sv3("uBHPos", *self.scene.bh_pos)
                self.sh_bh.sf("uRs", rs); self.sh_bh.si("uObjectID", 7)
                glBindVertexArray(self.sphere_vao)
                glDrawElements(GL_TRIANGLES, self.sphere_count, GL_UNSIGNED_INT, None)

                if self.scene.accretion_disk:
                    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                    self.sh_accretion.use()
                    self.sh_accretion.sm4("uView", view); self.sh_accretion.sm4("uProj", proj)
                    self.sh_accretion.sf("uRs", rs)
                    self.scene.accretion_disk.draw()
                    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # ─── Rebirth particles (HAWKING through NEW_WORLD) ───
            if HAWKING <= st <= NEW_WORLD and self.scene.rp.active > 0:
                glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                self.sh_rebirth.use()
                self.sh_rebirth.sm4("uView", view); self.sh_rebirth.sm4("uProj", proj)
                self.scene.rp.draw()
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # ─── Big Bang sphere ───
            if st == BIG_BANG and self.scene.bang_radius > 0.1:
                glEnable(GL_BLEND); glDepthMask(GL_FALSE)
                self.sh_bang.use()
                self.sh_bang.sm4("uView", view); self.sh_bang.sm4("uProj", proj)
                r = self.scene.bang_radius
                self.sh_bang.sm4("uModel", S(r, r, r))
                self.sh_bang.sf("uRadius", r)
                self.sh_bang.sf("uTime", self.scene.phase_t)
                self.sh_bang.sf("uAlpha", 1.0)
                self.sh_bang.sv3("uCoreCol", 1.0, 0.95, 0.6)
                self.sh_bang.sv3("uEdgeCol", 1.0, 0.3, 0.0)
                glBindVertexArray(self.sphere_vao)
                glDrawElements(GL_TRIANGLES, self.sphere_count, GL_UNSIGNED_INT, None)
                glDepthMask(GL_TRUE)

            # ─── Quark Plasma fullscreen ───
            if st == QUARK_PLASMA:
                glDisable(GL_DEPTH_TEST)
                self.sh_plasma.use()
                self.sh_plasma.sf("uTime", self.scene.phase_t)
                t_frac = self.scene.phase_t / (PHASE_DURATIONS[st] / self.scene.rebirth_speed)
                self.sh_plasma.sf("uAmplitude", 1.0 - t_frac * 0.4)
                self.sh_plasma.sf("uSpeed", 1.0)
                self.sh_plasma.sv3("uColA", 1.0, 1.0, 0.9)
                self.sh_plasma.sv3("uColB", 1.0, 0.35, 0.0)
                self.sh_plasma.sv3("uColC", 0.8, 0.05, 0.0)
                self.sh_plasma.sf("uAlpha", 0.9)
                self.hdr.draw_quad()
                glEnable(GL_DEPTH_TEST)

            # ─── First Stars: render glowing spheres ───
            if st == FIRST_STARS:
                self.sh_obj.use()
                self.sh_obj.sm4("uView", view); self.sh_obj.sm4("uProj", proj)
                self.sh_obj.sv3("uSunDir", 0,1,0); self.sh_obj.sv3("uSunCol", 5,5,5)
                self.sh_obj.si("uObjectID", 0)
                for s_data in self.scene.star_ignitions:
                    sc = s_data['scale']
                    if sc < 0.001: continue
                    self.sh_obj.sm4("uModel", T(*s_data['pos']) @ S(sc, sc, sc))
                    glActiveTexture(GL_TEXTURE0)
                    glBindTexture(GL_TEXTURE_2D, self.scene.objects[0].texture)
                    self.sh_obj.si("uTex", 0)
                    glBindVertexArray(self.sphere_vao)
                    glDrawElements(GL_TRIANGLES, self.sphere_count, GL_UNSIGNED_INT, None)

            # ─── Grid (NORMAL, DEVOUR, HAWKING, NEW_WORLD) ───
            if st in (NORMAL, APPROACH, SINGULARITY, DEVOUR, HAWKING, NEW_WORLD):
                self.sh_grid.use()
                self.sh_grid.sm4("uView", view); self.sh_grid.sm4("uProj", proj)
                self.sh_grid.sf("uOpacity", self.scene.grid_opacity)
                self.sh_grid.sf("uGravityScale", self.gravity_scale)

                attractors = []
                mass_vals = []
                
                # Only Earth should curve space-time in Normal mode (per user request)
                if st in (NORMAL, NEW_WORLD):
                    if len(self.scene.objects) > 0 and self.scene.objects[0].state != "GONE":
                        attractors.append(self.scene.objects[0].pos)
                        mass_vals.append(15.0) # Earth mass
                else:
                    # In collapse/devour phases, everything affects curvature
                    for obj in self.scene.planets:
                        if obj.state != "GONE":
                            attractors.append(obj.pos)
                            mass_vals.append(8.0)
                    if self.scene.bh_rs > 0.01:
                        attractors.append(self.scene.bh_pos)
                        mass_vals.append(50.0)
                    # Even in devour, maybe user still just want Earth? 
                    # No, usually black hole should curvature.
                    # But if we strictly follow "just for the earth", we'd skip others.
                    # However, usually users mean "remove the moon's curve".

                for i, (a, m) in enumerate(zip(attractors[:8], mass_vals[:8])):
                    self.sh_grid.sv3(f"uAttractors[{i}]", a[0], a[1], a[2])
                    self.sh_grid.sf(f"uMasses[{i}]", m)
                self.sh_grid.si("uNAttractors", len(attractors[:8]))
                self.sh_grid.sm4("uModel", T(0, self.grid_height, 0))
                glBindVertexArray(self.scene.grid_vao)
                glDrawArrays(GL_LINES, 0, self.scene.grid_count)

            # Orbit Rings
            if self.show_orbits and st in (NORMAL, NEW_WORLD):
                glEnable(GL_BLEND)
                self.sh_stars.use()
                self.sh_stars.sm4("uView", view); self.sh_stars.sm4("uProj", proj)
                if len(self.scene.objects) > 0:
                    self.sh_stars.sm4("uModel", T(*self.scene.objects[0].pos))
                    for ring_vao, ring_count in self.scene.rings:
                        glBindVertexArray(ring_vao)
                        glDrawArrays(GL_LINE_STRIP, 0, ring_count)

            # ─── Post Process ───
            bh_ndc = self.project_bh(self.scene.bh_pos, view, proj)
            rs_screen = self.scene.bh_rs / max(self.camera.dist, 0.1)
            lens_on = self.lens_strength if (SINGULARITY <= st <= HAWKING and self.scene.bh_rs > 0.01) else 0.0
            self.hdr.lensing_pass(self.sh_lensing, bh_ndc, rs_screen, lens_on)
            bloom_tex = self.hdr.bloom_pass(self.sh_blur, 8)

            self.hdr.composite(self.sh_composite, self.exposure, self.bloom_str, bloom_tex)
            self.sh_composite.use()
            self.sh_composite.sf("uFlash", self.scene.flash_alpha)
            self.hdr.draw_quad()

            self.render_ui()
            glfw.swap_buffers(self.window)

        self.impl.shutdown()
        glfw.terminate()

    def project_bh(self, pos, view, proj):
        p = proj @ view @ np.array([*pos, 1.0], dtype=np.float32)
        if p[3] == 0: return [0.5, 0.5]
        ndc = p[:2] / p[3]
        return (ndc + 1.0) / 2.0

if __name__ == "__main__":
    sim = Simulator()
    sim.run()
