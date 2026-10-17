"""The simulated world: robot pose, differential-drive physics, collisions,
bean bags, scoring, and sensor queries.

Threading model: step() runs on the main thread only. User code (worker
threads) calls the query methods; _lock guards the mutable pose/bag state
they read.
"""

from __future__ import annotations

import math
import random
import threading

from . import field, runtime
from .config import SimConfig
from .geometry import (AABB, Circle, normalize_deg, oriented_rect_corners,
                       poly_circle_collide, polys_collide, ray_circle,
                       ray_segment, signed_err_deg)

_IN_PER_MM = 1 / 25.4


class InputState:
    """Keyboard-driven inputs, written by the render loop each frame."""

    def __init__(self):
        self.axes = {"A": 0, "B": 0, "C": 0, "D": 0}
        self.buttons = {}            # controller button name -> bool
        self.brain_buttons = {"left": False, "check": False, "right": False}
        self.touchleds: set[int] = set()


class World:
    def __init__(self, clock, config: SimConfig):
        self.clock = clock
        self.config = config
        self._lock = threading.Lock()

        r = config.robot
        self.x = r.start_x
        self.y = r.start_y
        self.theta = r.start_theta_deg      # math convention, CCW+, continuous
        self._theta0 = r.start_theta_deg
        self.v = 0.0                        # in/s, + forward
        self.omega = 0.0                    # deg/s, CCW+

        self.bags = field.make_bags()
        self.carried: field.Bag | None = None
        if r.preload_yellow:
            preload = field.Bag("yellow", self.x, self.y, carried=True)
            self.bags.append(preload)
            self.carried = preload
        self.loads_remaining = config.skills_loads
        self._eject_cooldown_until = 0.0

        self.drivetrain = None              # vex.DriveTrain (latest constructed)
        self.brain = None                   # vex.Brain
        self.input = InputState()

        self.front_blocked = False
        self.collided = False
        self.program_status = "running"
        self.program_stop_requested = False

        self._last_ray_mm: float | None = None
        self._ray_closing_mps = 0.0

        self.score = {"red": 0, "blue": 0}

        self._solid_rect_polys = [rect.corners() for rect in
                                  field.solid_rects(r.height_in, r.strips_block)]
        self._solid_circles = field.solid_circles()
        self._bag_rect_polys = [rect.corners() for rect in field.bag_blocking_rects()]
        self._strip_polys = ([] if r.strips_block else
                             [rect.corners() for rect in field.STRIPS])
        self._dist_segs = field.distance_visible_segments(r.dist_height_in)
        self._dist_circles = field.distance_visible_circles()

    # ================= attachment from the vex module =================

    def attach_drivetrain(self, dt):
        if self.drivetrain is not None:
            print("[vexsim] note: more than one DriveTrain constructed; the last one drives the robot")
        self.drivetrain = dt

    def attach_brain(self, brain):
        self.brain = brain

    def request_program_stop(self):
        self.program_stop_requested = True

    # ================= queries used by the vex module =================

    def cw_rotation_deg(self) -> float:
        with self._lock:
            return self._theta0 - self.theta

    def omega_dps(self) -> float:
        return self.omega

    def heading_noise_deg(self) -> float:
        sigma = self.config.realism.heading_noise_deg
        return random.gauss(0.0, sigma) if sigma > 0 else 0.0

    def robot_poly(self):
        with self._lock:
            return oriented_rect_corners(self.x, self.y,
                                         self.config.robot.length_in,
                                         self.config.robot.width_in, self.theta)

    def distance_raycast_mm(self) -> float | None:
        r = self.config.robot
        with self._lock:
            t = math.radians(self.theta)
            fx, fy = math.cos(t), math.sin(t)
            lx, ly = -math.sin(t), math.cos(t)
            ox = self.x + fx * r.dist_forward_in + lx * r.dist_lateral_in
            oy = self.y + fy * r.dist_forward_in + ly * r.dist_lateral_in
            ang = math.radians(self.theta + r.dist_facing_deg)
        dx, dy = math.cos(ang), math.sin(ang)
        best = None
        for p1, p2 in self._dist_segs:
            t_hit = ray_segment(ox, oy, dx, dy, p1, p2)
            if t_hit is not None and (best is None or t_hit < best):
                best = t_hit
        for c in self._dist_circles:
            t_hit = ray_circle(ox, oy, dx, dy, c)
            if t_hit is not None and (best is None or t_hit < best):
                best = t_hit
        if best is None:
            return None
        mm = best * 25.4
        sigma = self.config.realism.distance_noise_mm
        if sigma > 0:
            mm += random.gauss(0.0, sigma)
        mm = max(mm, 20.0)
        if mm > r.dist_max_range_mm:
            return None
        return mm

    def distance_closing_mps(self) -> float:
        return self._ray_closing_mps

    def bumper_pressing(self) -> bool:
        return self.front_blocked

    def bag_color_in_front(self) -> str | None:
        """Color of the nearest bag in the pickup zone (optical/intake)."""
        bag = self._bag_in_pickup_zone()
        return bag.color if bag else None

    def brain_button_pressing(self, name: str) -> bool:
        return self.input.brain_buttons.get(name, False)

    def touchled_pressing(self, index: int) -> bool:
        return index in self.input.touchleds

    def controller_axis(self, name: str) -> int:
        return self.input.axes.get(name, 0)

    def controller_button(self, name: str) -> bool:
        return self.input.buttons.get(name, False)

    # ================= helpers =================

    def _bag_in_pickup_zone(self) -> field.Bag | None:
        r = self.config.robot
        with self._lock:
            x, y, theta = self.x, self.y, self.theta
        t = math.radians(theta)
        fx, fy = math.cos(t), math.sin(t)
        lx, ly = -math.sin(t), math.cos(t)
        best = None
        best_d = 1e9
        for bag in self.bags:
            if bag.carried:
                continue
            relx = bag.x - x
            rely = bag.y - y
            fwd = relx * fx + rely * fy
            lat = relx * lx + rely * ly
            if (r.length_in / 2 - 1.5 <= fwd <= r.length_in / 2 + r.pickup_reach_in
                    and abs(lat) <= r.pickup_halfwidth_in):
                if fwd < best_d:
                    best_d = fwd
                    best = bag
        return best

    def _collides(self, poly) -> bool:
        for solid in self._solid_rect_polys:
            if polys_collide(poly, solid):
                return True
        for c in self._solid_circles:
            if poly_circle_collide(poly, c):
                return True
        # perimeter: any corner outside the field
        for px, py in poly:
            if not (0.0 <= px <= field.FIELD_W and 0.0 <= py <= field.FIELD_H):
                return True
        return False

    def _drive_motor_speeds(self):
        """Wheel linear speeds (vl, vr) in in/s from motor state, and the
        geometry (track width in inches) to use."""
        cfg = self.config.robot
        dt = self.drivetrain
        if dt is not None:
            lm = dt.lm.motors[0] if hasattr(dt.lm, "motors") else dt.lm
            rm = dt.rm.motors[0] if hasattr(dt.rm, "motors") else dt.rm
            travel = dt.wheel_travel_in * dt.gear_ratio
            vl = lm._actual_dps / 360.0 * travel
            vr = rm._actual_dps / 360.0 * travel
            return vl, vr, dt.track_width_in
        # fallback: raw motors on configured ports
        if cfg.left_drive_ports and cfg.right_drive_ports:
            travel = cfg.fallback_wheel_travel_mm * _IN_PER_MM
            track = cfg.fallback_track_width_mm * _IN_PER_MM
            vl = vr = 0.0
            for dev in runtime.devices:
                port = getattr(dev, "port", None)
                dps = getattr(dev, "_actual_dps", None)
                if dps is None:
                    continue
                if port in cfg.left_drive_ports:
                    vl += dps / 360.0 * travel
                if port in cfg.right_drive_ports:
                    vr += dps / 360.0 * travel
            return vl, vr, track
        return 0.0, 0.0, cfg.fallback_track_width_mm * _IN_PER_MM

    # ================= the physics step =================

    def step(self, dt_s: float) -> None:
        # substep for stability
        remaining = dt_s
        while remaining > 1e-9:
            h = min(remaining, 1 / 120.0)
            self._substep(h)
            remaining -= h

    def _substep(self, h: float) -> None:
        import vex  # safe: vex is fully imported before the loop starts

        self._apply_drivetrain_command(vex)
        self._integrate_motors(h)
        self._move_robot(h)
        self._update_drivetrain_progress(vex, h)
        self._update_bags()
        self._update_score()
        self._update_ray(h)
        self._debug_trace()

    _next_trace = 0.0

    def _debug_trace(self) -> None:
        import os
        if not os.environ.get("VEXSIM_DEBUG"):
            return
        if self.clock.now() < self._next_trace:
            return
        self._next_trace = self.clock.now() + 0.25
        dt = self.drivetrain
        if dt is None or dt._cmd is None:
            return
        cmd = dt._cmd
        lm = dt.lm.motors[0] if hasattr(dt.lm, "motors") else dt.lm
        rm = dt.rm.motors[0] if hasattr(dt.rm, "motors") else dt.rm
        print(f"[dbg] t={self.clock.now():6.2f} {cmd.kind:9s} done={cmd.done} "
              f"rem_in={cmd.remaining_in:7.2f} rem_deg={cmd.remaining_deg:7.2f} "
              f"lm cmd={lm._cmd_dps:7.1f} act={lm._actual_dps:7.1f} mode={lm._mode} "
              f"rm cmd={rm._cmd_dps:7.1f} act={rm._actual_dps:7.1f} mode={rm._mode} "
              f"blocked={self.collided} pose=({self.x:5.1f},{self.y:5.1f},{self.theta:7.1f})")

    # ---- drivetrain command -> drive motor velocity targets ----

    def _apply_drivetrain_command(self, vex) -> None:
        dt = self.drivetrain
        if dt is None or dt._cmd is None or dt._cmd.done:
            return
        cmd = dt._cmd

        # timeout
        if cmd.deadline is not None and self.clock.now() >= cmd.deadline:
            self._finish_command(dt, cmd, timed_out=True)
            return

        lm = dt.lm.motors[0] if hasattr(dt.lm, "motors") else dt.lm
        max_dps = 720.0 * lm.gear_ratio  # wheel-shaft dps at 100%
        base = min(abs(cmd.vel_pct), 100.0) / 100.0 * max_dps

        if cmd.kind in ("drive", "drive_for"):
            scale = 1.0
            if cmd.kind == "drive_for" and cmd.remaining_in < 2.0:
                scale = max(0.25, cmd.remaining_in / 2.0)  # decelerate to stop on target
            dps = cmd.sign * base * scale
            self._set_drive_dps(dt, dps, dps)
        else:  # turn / turn_for / turn_to
            if cmd.kind == "turn_to":
                sensor = dt._heading_sensor()
                if cmd.target_is_rotation:
                    err = cmd.target_cw - sensor.rotation(vex.DEGREES)
                else:
                    err = signed_err_deg(cmd.target_cw, sensor.heading(vex.DEGREES))
                cmd.cw_sign = 1.0 if err >= 0 else -1.0
                scale = min(1.0, abs(err) / (25.0 / dt._turn_constant))
            elif cmd.kind == "turn_for":
                scale = min(1.0, max(0.2, cmd.remaining_deg / 20.0))
            else:
                scale = 1.0
            wheel_dps = base * scale
            if cmd.kind != "turn":
                wheel_dps = min(max(wheel_dps, 30.0), base)  # floor so turns settle
            # clockwise turn: left wheel forward, right wheel back
            self._set_drive_dps(dt, cmd.cw_sign * wheel_dps, -cmd.cw_sign * wheel_dps)

    def _set_drive_dps(self, dt, left_dps, right_dps):
        for m, dps in ((dt.lm, left_dps), (dt.rm, right_dps)):
            motors = m.motors if hasattr(m, "motors") else [m]
            for motor in motors:
                motor._mode = "vel"
                motor._cmd_dps = dps
                motor._done = False

    def _finish_command(self, dt, cmd, timed_out=False):
        cmd.done = True
        self._set_drive_dps(dt, 0.0, 0.0)
        for m in (dt.lm, dt.rm):
            motors = m.motors if hasattr(m, "motors") else [m]
            for motor in motors:
                motor._mode = "idle"
                motor._done = True
                motor._actual_dps = 0.0  # BRAKE: stop dead so the next move starts straight
        # turn overshoot realism knob
        if not timed_out and cmd.kind in ("turn_for", "turn_to"):
            knob = self.config.realism.turn_overshoot_deg
            if knob > 0:
                extra = abs(random.gauss(knob, knob / 2))
                with self._lock:
                    self.theta -= cmd.cw_sign * extra  # cw overshoot continues the turn

    # ---- motor integration ----

    def _integrate_motors(self, h: float) -> None:
        accel = self.config.robot.motor_accel_dps2
        for dev in runtime.devices:
            if not hasattr(dev, "_actual_dps"):
                continue
            m = dev
            if m._mode == "pos":
                err = m._target_pos - m._pos
                arrive_dps = abs(err) / h if h > 0 else 0.0
                desired = math.copysign(min(abs(m._cmd_dps), arrive_dps), err)
                if abs(err) < 0.5:
                    m._pos = m._target_pos
                    m._actual_dps = 0.0
                    m._mode = "idle"
                    m._done = True
                    continue
            elif m._mode == "vel":
                desired = m._cmd_dps
            else:
                desired = 0.0
            delta = desired - m._actual_dps
            max_delta = accel * h
            if abs(delta) > max_delta:
                delta = math.copysign(max_delta, delta)
            m._actual_dps += delta
            m._pos += m._actual_dps * h

    # ---- robot motion + collision ----

    def _move_robot(self, h: float) -> None:
        vl, vr, track = self._drive_motor_speeds()
        slip = self.config.realism.wheel_slip
        if slip > 0:
            vl *= 1.0 - random.uniform(0, slip)
            vr *= 1.0 - random.uniform(0, slip)

        v = (vl + vr) / 2.0
        omega = math.degrees((vr - vl) / max(track, 1.0))

        with self._lock:
            x0, y0, theta0 = self.x, self.y, self.theta

        # climbing a ramped floor strip slows the robot down
        if self._strip_polys:
            cfg0 = self.config.robot
            poly0 = oriented_rect_corners(x0, y0, cfg0.length_in, cfg0.width_in, theta0)
            for strip in self._strip_polys:
                if polys_collide(poly0, strip):
                    v *= cfg0.strip_slow_factor
                    omega *= cfg0.strip_slow_factor
                    break
        t = math.radians(theta0)
        nx = x0 + v * math.cos(t) * h
        ny = y0 + v * math.sin(t) * h
        ntheta = theta0 + omega * h

        cfg = self.config.robot
        blocked = False
        poly = oriented_rect_corners(nx, ny, cfg.length_in, cfg.width_in, ntheta)
        if not self._collides(poly):
            fx, fy, ftheta = nx, ny, ntheta
        else:
            # try rotation only
            poly = oriented_rect_corners(x0, y0, cfg.length_in, cfg.width_in, ntheta)
            if not self._collides(poly):
                fx, fy, ftheta = x0, y0, ntheta
                blocked = True
            else:
                fx, fy, ftheta = x0, y0, theta0
                blocked = True

        with self._lock:
            self.x, self.y, self.theta = fx, fy, ftheta
            self.v = v if not blocked else 0.0
            self.omega = (ftheta - theta0) / h if h > 0 else 0.0
            self._actual_ds = math.hypot(fx - x0, fy - y0) * (1 if v >= 0 else -1)
            self._actual_dtheta_cw = -(ftheta - theta0)
        self.collided = blocked
        self.front_blocked = blocked and v > 0.01

    # ---- command progress ----

    def _update_drivetrain_progress(self, vex, h: float) -> None:
        dt = self.drivetrain
        if dt is None or dt._cmd is None or dt._cmd.done:
            return
        cmd = dt._cmd
        if cmd.kind == "drive_for":
            cmd.remaining_in -= abs(self._actual_ds)
            if cmd.remaining_in <= 0:
                self._finish_command(dt, cmd)
        elif cmd.kind == "turn_for":
            cmd.remaining_deg -= abs(self._actual_dtheta_cw)
            if cmd.remaining_deg <= 0:
                self._finish_command(dt, cmd)
        elif cmd.kind == "turn_to":
            sensor = dt._heading_sensor()
            if cmd.target_is_rotation:
                err = cmd.target_cw - sensor.rotation(vex.DEGREES)
            else:
                err = signed_err_deg(cmd.target_cw, sensor.heading(vex.DEGREES))
            if abs(err) <= dt._turn_threshold:
                self._finish_command(dt, cmd)

    # ---- bean bags ----

    def _intake_dps(self) -> float:
        total = 0.0
        for dev in runtime.devices:
            if getattr(dev, "port", None) in self.config.robot.intake_ports \
                    and hasattr(dev, "_actual_dps"):
                total += dev._actual_dps
        return total

    def _update_bags(self) -> None:
        cfg = self.config.robot
        with self._lock:
            x, y, theta = self.x, self.y, self.theta
        t = math.radians(theta)
        fx, fy = math.cos(t), math.sin(t)

        intake = self._intake_dps()
        now = self.clock.now()

        # carried bag follows the robot's front
        if self.carried is not None:
            self.carried.x = x + fx * (cfg.length_in / 2 - 1.0)
            self.carried.y = y + fy * (cfg.length_in / 2 - 1.0)

        if intake > 30.0 and self.carried is None and now >= self._eject_cooldown_until:
            bag = self._bag_in_pickup_zone()
            if bag is not None:
                bag.carried = True
                self.carried = bag
        elif intake < -30.0 and self.carried is not None:
            bag = self.carried
            bag.carried = False
            bag.x = x + fx * (cfg.length_in / 2 + 2.5)
            bag.y = y + fy * (cfg.length_in / 2 + 2.5)
            self._clamp_bag(bag)
            self.carried = None
            self._eject_cooldown_until = now + 0.8

        # robot pushes loose bags
        poly = oriented_rect_corners(x, y, cfg.length_in, cfg.width_in, theta)
        for bag in self.bags:
            if bag.carried:
                continue
            if polys_collide(poly, bag.aabb().corners()):
                self._push_bag(bag, x, y, poly)

    def _push_bag(self, bag, rx, ry, robot_poly) -> None:
        dx = bag.x - rx
        dy = bag.y - ry
        norm = math.hypot(dx, dy)
        if norm < 1e-6:
            dx, dy, norm = 1.0, 0.0, 1.0
        dx, dy = dx / norm, dy / norm
        ox, oy = bag.x, bag.y
        for _ in range(40):
            bag.x += dx * 0.25
            bag.y += dy * 0.25
            if not polys_collide(robot_poly, bag.aabb().corners()):
                break
        if self._bag_stuck(bag):
            bag.x, bag.y = ox, oy  # pinned against something solid

    def _bag_stuck(self, bag) -> bool:
        bb = bag.aabb()
        if bb.x0 < 0 or bb.y0 < 0 or bb.x1 > field.FIELD_W or bb.y1 > field.FIELD_H:
            return True
        poly = bb.corners()
        for solid in self._bag_rect_polys:  # bags slide over strips, not pyramids
            if polys_collide(poly, solid):
                return True
        for c in self._solid_circles:
            if poly_circle_collide(poly, c):
                return True
        return False

    def _clamp_bag(self, bag) -> None:
        bag.x = min(max(bag.x, field.BAG_W / 2), field.FIELD_W - field.BAG_W / 2)
        bag.y = min(max(bag.y, field.BAG_H / 2), field.FIELD_H - field.BAG_H / 2)

    def add_load_bag(self) -> bool:
        """Drop a Skills load bag into the red Load Zone (keyboard 'b')."""
        if self.loads_remaining <= 0:
            return False
        color = "red" if self.loads_remaining % 2 == 0 else "blue"
        zone = field.LOAD_ZONES["red"]
        jitter = (self.loads_remaining % 4)
        bag = field.Bag(color, zone.cx, zone.cy - 4 + 3 * jitter)
        self.bags.append(bag)
        self.loads_remaining -= 1
        return True

    # ---- scoring ----

    def _update_score(self) -> None:
        score = {"red": 0, "blue": 0}
        for goal_color, zone in field.FLOOR_GOALS.items():
            for bag in self.bags:
                if bag.carried:
                    continue
                if bag.color in (goal_color, "yellow") and zone.contains_aabb(bag.aabb()):
                    score[goal_color] += 1
        self.score = score

    # ---- distance history for object_velocity ----

    def _update_ray(self, h: float) -> None:
        mm = self.distance_raycast_mm()
        if mm is not None and self._last_ray_mm is not None and h > 0:
            # + toward sensor (closing), in m/s
            self._ray_closing_mps = (self._last_ray_mm - mm) / 1000.0 / h
        else:
            self._ray_closing_mps = 0.0
        self._last_ray_mm = mm
