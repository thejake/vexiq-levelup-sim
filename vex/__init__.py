"""Fake `vex` module for the vexsim simulator.

Mirrors the VEX IQ 2nd-generation Python API (VEXcode IQ) closely enough
that programs written against it transfer to the real robot unchanged.
Reference: reference/vex_iq_api.md (compiled from https://api.vex.com/iq2/).

Anything the simulator does not model raises VexSimNotImplemented with a
clear message — it never silently no-ops.
"""

from __future__ import annotations

import math
import os
import sys
import threading
import traceback


def _maybe_reexec():
    """If a user program is run directly (`python myfile.py`), relaunch it
    under the simulator runner (`python -m vexsim myfile.py`)."""
    if os.environ.get("VEXSIM_ACTIVE") == "1":
        return
    main = sys.modules.get("__main__")
    script = getattr(main, "__file__", None)
    if not script or not os.path.isfile(script):
        return  # REPL, stdin, or embedded use: leave it alone
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = dict(os.environ)
    env["PYTHONPATH"] = repo_root + os.pathsep + env.get("PYTHONPATH", "")
    os.execve(sys.executable,
              [sys.executable, "-m", "vexsim", os.path.abspath(script)] + sys.argv[1:],
              env)


_maybe_reexec()

from vexsim import runtime as _rt
from vexsim.runtime import VexSimError, VexSimNotImplemented
from vexsim.geometry import normalize_deg as _normalize_deg, signed_err_deg as _signed_err_deg


def _clock():
    _rt.require_sim()
    return _rt.clock


def _world():
    return _rt.require_sim()


def _run_callback(callback, arg=()):
    """Run a user callback in its own daemon thread (VEX event semantics)."""
    def runner():
        try:
            callback(*arg)
        except BaseException:
            traceback.print_exc()
    threading.Thread(target=runner, daemon=True).start()


# ============================================================
# Enums and constants
# ============================================================

class vexEnum:
    def __init__(self, value, name):
        self.value = value
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self is other or (isinstance(other, vexEnum) and self.name == other.name)

    def __hash__(self):
        return hash(self.name)


def _make_enum(class_name, names):
    members = {}
    inner = type(class_name, (vexEnum,), {})
    cls_dict = {class_name: inner}
    for i, name in enumerate(names):
        member = inner(i, f"{class_name}.{name}")
        cls_dict[name] = member
        members[name] = member
    cls = type(class_name, (), cls_dict)
    return cls, members


PercentUnits, _m = _make_enum("PercentUnits", ["PERCENT"])
PERCENT = _m["PERCENT"]

TimeUnits, _m = _make_enum("TimeUnits", ["SECONDS", "MSEC"])
SECONDS = _m["SECONDS"]
MSEC = _m["MSEC"]

DistanceUnits, _m = _make_enum("DistanceUnits", ["MM", "IN", "CM"])
MM = _m["MM"]
INCHES = _m["IN"]

RotationUnits, _m = _make_enum("RotationUnits", ["DEG", "REV", "RAW"])
DEGREES = _m["DEG"]
TURNS = _m["REV"]

VelocityUnits, _m = _make_enum("VelocityUnits", ["PCT", "RPM", "DPS"])
RPM = _m["RPM"]
DPS = _m["DPS"]

TorqueUnits, _m = _make_enum("TorqueUnits", ["NM", "INLB"])
CurrentUnits, _m = _make_enum("CurrentUnits", ["AMP"])
AMP = _m["AMP"]
PowerUnits, _m = _make_enum("PowerUnits", ["WATT"])
TemperatureUnits, _m = _make_enum("TemperatureUnits", ["CELSIUS", "FAHRENHEIT"])
VoltageUnits, _m = _make_enum("VoltageUnits", ["VOLT", "MV"])
VOLT = _m["VOLT"]
MV = _m["MV"]

DirectionType, _m = _make_enum("DirectionType", ["FORWARD", "REVERSE"])
FORWARD = _m["FORWARD"]
REVERSE = _m["REVERSE"]

TurnType, _m = _make_enum("TurnType", ["LEFT", "RIGHT"])
LEFT = _m["LEFT"]
RIGHT = _m["RIGHT"]

BrakeType, _m = _make_enum("BrakeType", ["COAST", "BRAKE", "HOLD"])
COAST = _m["COAST"]
BRAKE = _m["BRAKE"]
HOLD = _m["HOLD"]

AxisType, _m = _make_enum("AxisType", ["XAXIS", "YAXIS", "ZAXIS"])
XAXIS = _m["XAXIS"]
YAXIS = _m["YAXIS"]
ZAXIS = _m["ZAXIS"]

OrientationType, _m = _make_enum("OrientationType", ["ROLL", "PITCH", "YAW"])
ROLL = _m["ROLL"]
PITCH = _m["PITCH"]
YAW = _m["YAW"]

ObjectSizeType, _m = _make_enum("ObjectSizeType", ["NONE", "SMALL", "MEDIUM", "LARGE"])

LedStateType, _m = _make_enum("LedStateType", ["OFF", "ON", "BLINK"])
FadeType, _m = _make_enum("FadeType", ["OFF", "SLOW", "FAST"])

GearSetting, _m = _make_enum("GearSetting", ["RATIO_1_1", "RATIO_2_1", "RATIO_3_1"])
_GEAR_RATIOS = {GearSetting.RATIO_1_1: 1.0, GearSetting.RATIO_2_1: 2.0,
                GearSetting.RATIO_3_1: 3.0}

FontType, _m = _make_enum("FontType", ["MONO12", "MONO15", "MONO20", "MONO30",
                                       "MONO40", "MONO60", "PROP20", "PROP30",
                                       "PROP40", "PROP60"])

SoundType, _m = _make_enum("SoundType", [
    "SIREN", "WRONG_WAY", "WRONG_WAY_SLOW", "FILLUP", "HEADLIGHTS_ON",
    "HEADLIGHTS_OFF", "TOLLBOOTH", "ALARM", "TADA", "DOOR_CLOSE", "RATCHET",
    "WRENCH", "SIREN2", "RATCHET2", "ALARM2", "POWER_DOWN"])

CylinderType, _m = _make_enum("CylinderType", ["CYLINDER1", "CYLINDER2", "CYLINDERALL"])
CYLINDER1 = _m["CYLINDER1"]
CYLINDER2 = _m["CYLINDER2"]
CYLINDERALL = _m["CYLINDERALL"]


class Ports:
    PORT1, PORT2, PORT3, PORT4, PORT5, PORT6 = 1, 2, 3, 4, 5, 6
    PORT7, PORT8, PORT9, PORT10, PORT11, PORT12 = 7, 8, 9, 10, 11, 12


PORT1, PORT2, PORT3, PORT4, PORT5, PORT6 = 1, 2, 3, 4, 5, 6
PORT7, PORT8, PORT9, PORT10, PORT11, PORT12 = 7, 8, 9, 10, 11, 12


class Color:
    class DefinedColor:
        def __init__(self, rgb, name="color"):
            self._rgb = rgb
            self.name = name

        def __repr__(self):
            return self.name

    def __init__(self, *args):
        if len(args) == 1:
            v = args[0]
            if isinstance(v, str):
                v = int(v.lstrip("#"), 16)
            self._rgb = ((v >> 16) & 255, (v >> 8) & 255, v & 255)
        elif len(args) == 3:
            self._rgb = tuple(args)
        else:
            raise TypeError("Color(value) or Color(r, g, b)")
        self.name = "Color(custom)"

    def rgb(self, r, g, b):
        self._rgb = (r, g, b)

    def hsv(self, h, s, v):
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
        self._rgb = (int(r * 255), int(g * 255), int(b * 255))

    def web(self, value):
        v = int(value.lstrip("#"), 16)
        self._rgb = ((v >> 16) & 255, (v >> 8) & 255, v & 255)


def _defined(name, rgb):
    c = Color.DefinedColor(rgb, f"Color.{name}")
    setattr(Color, name, c)
    return c


_defined("BLACK", (0, 0, 0))
_defined("WHITE", (255, 255, 255))
_defined("RED", (255, 0, 0))
_defined("GREEN", (0, 255, 0))
_defined("BLUE", (0, 80, 255))
_defined("YELLOW", (255, 220, 0))
_defined("ORANGE", (255, 140, 0))
_defined("PURPLE", (160, 32, 240))
_defined("CYAN", (0, 255, 255))
_defined("TRANSPARENT", (16, 16, 16))
_defined("RED_VIOLET", (199, 21, 133))
_defined("VIOLET", (138, 43, 226))
_defined("BLUE_VIOLET", (92, 60, 230))
_defined("BLUE_GREEN", (13, 152, 186))
_defined("YELLOW_GREEN", (154, 205, 50))
_defined("YELLOW_ORANGE", (255, 174, 66))
_defined("RED_ORANGE", (255, 83, 73))


# ============================================================
# Unit conversions
# ============================================================

_MM_PER_IN = 25.4


def _dist_to_inches(value, units):
    if units is MM:
        return value / _MM_PER_IN
    if units is INCHES:
        return float(value)
    if units is DistanceUnits.CM:
        return value * 10.0 / _MM_PER_IN
    raise VexSimError(f"unknown distance units {units!r}")


def _inches_to_dist(value_in, units):
    if units is MM:
        return value_in * _MM_PER_IN
    if units is INCHES:
        return value_in
    if units is DistanceUnits.CM:
        return value_in * _MM_PER_IN / 10.0
    raise VexSimError(f"unknown distance units {units!r}")


def _rot_to_deg(value, units):
    if units is DEGREES:
        return float(value)
    if units is TURNS:
        return value * 360.0
    raise VexSimError(f"unknown rotation units {units!r}")


def _deg_to_rot(value_deg, units):
    if units is DEGREES:
        return value_deg
    if units is TURNS:
        return value_deg / 360.0
    raise VexSimError(f"unknown rotation units {units!r}")


def _time_to_s(value, units):
    if units is MSEC:
        return value / 1000.0
    if units is SECONDS:
        return float(value)
    raise VexSimError(f"unknown time units {units!r}")


_MOTOR_MAX_RPM = 120.0  # IQ smart motor free speed


def _vel_to_pct(value, units):
    """Convert a velocity in the given units to percent of motor max."""
    if units is None or units is PERCENT or units is VelocityUnits.PCT:
        return float(value)
    if units is RPM:
        return value / _MOTOR_MAX_RPM * 100.0
    if units is DPS:
        return value / (_MOTOR_MAX_RPM * 6.0) * 100.0
    raise VexSimError(f"unknown velocity units {units!r}")


def _pct_to_vel(pct, units):
    if units is None or units is PERCENT or units is VelocityUnits.PCT:
        return pct
    if units is RPM:
        return pct / 100.0 * _MOTOR_MAX_RPM
    if units is DPS:
        return pct / 100.0 * _MOTOR_MAX_RPM * 6.0
    raise VexSimError(f"unknown velocity units {units!r}")


# ============================================================
# wait / sleep / Thread / Event / Timer
# ============================================================

def wait(time, units=MSEC):
    """Block this thread for the given SIMULATED time."""
    _clock().sleep(_time_to_s(time, units))


def sleep(time, units=MSEC):
    """Undocumented alias for wait() used by VEXcode-generated code."""
    wait(time, units)


class Thread:
    def __init__(self, callback, arg=()):
        self._thread = threading.Thread(
            target=self._run, args=(callback, arg), daemon=True)
        self._thread.start()

    @staticmethod
    def _run(callback, arg):
        try:
            callback(*arg)
        except BaseException:
            traceback.print_exc()

    def stop(self):
        raise VexSimNotImplemented(
            "Thread.stop()",
            "Python threads can't be killed; have the thread check a flag and return.")


class Event:
    def __init__(self, callback=None, args=()):
        self._registered = []
        if callback is not None:
            self._registered.append((callback, args))

    def __call__(self, callback, args=()):
        self._registered.append((callback, args))

    def set(self, callback, args=()):
        self._registered.append((callback, args))

    def broadcast(self):
        for callback, args in self._registered:
            _run_callback(callback, args)

    def broadcast_and_wait(self):
        threads = []
        for callback, args in self._registered:
            t = threading.Thread(target=Thread._run, args=(callback, args), daemon=True)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()


class Timer:
    def __init__(self):
        self._start = _clock().now()

    def time(self, units=MSEC):
        elapsed = _clock().now() - self._start
        return elapsed * 1000.0 if units is MSEC else elapsed

    def clear(self):
        self._start = _clock().now()

    def system(self):
        return _clock().now_ms()

    def system_high_res(self):
        return _clock().now() * 1_000_000.0

    def event(self, callback, delay, arg=()):
        def waiter():
            _clock().sleep(delay / 1000.0)
            callback(*arg)
        threading.Thread(target=waiter, daemon=True).start()


def _poll_changed(read_value, callback, arg=(), period_s=0.05):
    """Background poller implementing .changed(callback) semantics."""
    def poller():
        try:
            last = read_value()
            while True:
                _clock().sleep(period_s)
                current = read_value()
                if current != last:
                    last = current
                    _run_callback(callback, arg)
        except SystemExit:
            pass
        except BaseException:
            traceback.print_exc()
    threading.Thread(target=poller, daemon=True).start()


class _PressWatcher:
    """Shared pressed()/released() callback plumbing for anything with a
    boolean 'is pressed now' state."""

    def __init__(self, read_pressing):
        self._read = read_pressing
        self._press_cbs = []
        self._release_cbs = []
        self._started = False

    def on_pressed(self, callback, arg=()):
        self._press_cbs.append((callback, arg))
        self._ensure()

    def on_released(self, callback, arg=()):
        self._release_cbs.append((callback, arg))
        self._ensure()

    def _ensure(self):
        if self._started:
            return
        self._started = True

        def poller():
            try:
                last = bool(self._read())
                while True:
                    _clock().sleep(0.02)
                    current = bool(self._read())
                    if current and not last:
                        for cb, arg in self._press_cbs:
                            _run_callback(cb, arg)
                    elif last and not current:
                        for cb, arg in self._release_cbs:
                            _run_callback(cb, arg)
                    last = current
            except SystemExit:
                pass
            except BaseException:
                traceback.print_exc()
        threading.Thread(target=poller, daemon=True).start()


# ============================================================
# Motor / MotorGroup
# ============================================================

class Motor:
    """Simulated IQ smart motor.

    Engine contract (read/written by vexsim.world each tick):
      _mode: 'idle' | 'vel' | 'pos'
      _cmd_dps: signed target output speed (deg/s), + = logical FORWARD
      _target_pos: absolute target (output deg) for 'pos' mode
      _pos: current position (output deg)
      _actual_dps: what the motor actually did last tick
      _done: last spin_for/spin_to_position finished
    """

    def __init__(self, port, *args, **kwargs):
        self.port = port
        gears = kwargs.pop("gears", None)
        reverse = kwargs.pop("reverse", None)
        if kwargs:
            raise TypeError(f"Motor: unexpected kwargs {list(kwargs)}")
        # Accept all real-world forms: Motor(p), Motor(p, True),
        # Motor(p, 1.5, True), Motor(p, GearSetting.RATIO_2_1, False)
        for a in args:
            if isinstance(a, bool):
                reverse = a
            elif isinstance(a, (int, float)):
                gears = float(a)
            elif isinstance(a, vexEnum) and a in _GEAR_RATIOS:
                gears = _GEAR_RATIOS[a]
            else:
                raise TypeError(f"Motor: can't interpret argument {a!r}")
        self.gear_ratio = float(gears) if gears else 1.0
        self.reversed = bool(reverse)

        self._mode = "idle"
        self._cmd_dps = 0.0
        self._target_pos = 0.0
        self._pos = 0.0
        self._pos_offset = 0.0
        self._actual_dps = 0.0
        self._done = True
        self._velocity_pct = 50.0     # default at project start
        self._max_torque_pct = 50.0
        self._stopping = BRAKE
        self._timeout_s = None
        _rt.register(self)

    # -- internals --

    def _max_out_dps(self):
        return _MOTOR_MAX_RPM * 6.0 * self.gear_ratio

    def _signed_pct(self, direction, velocity, units_v):
        pct = self._velocity_pct if velocity is None else _vel_to_pct(velocity, units_v)
        if direction is REVERSE:
            pct = -pct
        elif direction is not FORWARD:
            raise VexSimError(f"direction must be FORWARD or REVERSE, got {direction!r}")
        return pct

    # -- actions --

    def spin(self, direction, velocity=None, units=None):
        self._spin_sign = -1.0 if direction is REVERSE else 1.0
        pct = self._signed_pct(direction, velocity, units)
        self._cmd_dps = pct / 100.0 * self._max_out_dps()
        self._mode = "vel"
        self._done = False

    def spin_for(self, direction, angle, units=DEGREES, velocity=None,
                 units_v=None, wait=True):
        delta = _rot_to_deg(angle, units)
        # docs: units_v defaults to RPM for spin_for
        pct = self._signed_pct(direction, velocity,
                               units_v if units_v is not None else RPM)
        if pct < 0:
            delta = -delta
        self._target_pos = self._pos + delta
        self._cmd_dps = abs(pct) / 100.0 * self._max_out_dps()
        self._mode = "pos"
        self._done = False
        if wait:
            self._wait_done()

    def spin_to_position(self, rotation, units=DEGREES, velocity=None,
                         units_v=None, wait=True):
        pct = abs(self._velocity_pct if velocity is None
                  else _vel_to_pct(velocity, units_v if units_v is not None else RPM))
        self._target_pos = _rot_to_deg(rotation, units) - self._pos_offset
        self._cmd_dps = pct / 100.0 * self._max_out_dps()
        self._mode = "pos"
        self._done = False
        if wait:
            self._wait_done()

    def _wait_done(self):
        finished = _clock().wait_for(lambda: self._done, timeout=self._timeout_s)
        if not finished:
            self.stop()

    def stop(self, mode=None):
        self._mode = "idle"
        self._cmd_dps = 0.0
        self._done = True
        if mode is not None:
            self._stopping = mode

    # -- mutators --

    def set_velocity(self, velocity, units=None):
        # A negative velocity composes with the spin() direction — real code
        # uses set_velocity(-100, PERCENT) then spin(FORWARD) to reverse.
        self._velocity_pct = _vel_to_pct(velocity, units)
        if self._mode == "vel":
            self._cmd_dps = self._spin_sign * self._velocity_pct / 100.0 * self._max_out_dps()

    def set_max_torque(self, value, units=PERCENT):
        _rt.note_once("max_torque", "set_max_torque recorded but the simulator has no stall/torque model")
        self._max_torque_pct = value

    def set_position(self, position, units=DEGREES):
        self._pos_offset = _rot_to_deg(position, units) - self._pos

    def reset_position(self):
        self._pos_offset = -self._pos

    def set_stopping(self, mode):
        self._stopping = mode

    def set_timeout(self, value, units=MSEC):
        self._timeout_s = _time_to_s(value, units)

    def get_timeout(self):
        return 0 if self._timeout_s is None else self._timeout_s * 1000.0

    def set_reversed(self, value):
        self.reversed = bool(value)

    # -- getters --

    def position(self, units=DEGREES):
        return _deg_to_rot(self._pos + self._pos_offset, units)

    def velocity(self, units=RPM):
        pct = self._actual_dps / self._max_out_dps() * 100.0
        return _pct_to_vel(pct, units)

    def current(self, units=CurrentUnits.AMP):
        return 0.4 if self._mode != "idle" else 0.05

    def power(self):
        return abs(self._actual_dps) / self._max_out_dps() * 2.0

    def torque(self, units=TorqueUnits.NM):
        return 0.0

    def efficiency(self):
        return 65.0 if self._mode != "idle" else 0.0

    def temperature(self, units=TemperatureUnits.CELSIUS):
        return 25.0 if units is TemperatureUnits.CELSIUS else 77.0

    def is_done(self):
        return self._done

    def is_spinning(self):
        return not self._done or self._mode == "vel"

    def direction(self):
        if self._mode == "idle" or self._actual_dps == 0:
            return FORWARD
        return FORWARD if self._actual_dps > 0 else REVERSE

    def installed(self):
        return True

    # sign of the last spin() direction; set_velocity mid-spin composes with it
    _spin_sign = 1.0


class MotorGroup:
    def __init__(self, *motors):
        if not motors:
            raise VexSimError("MotorGroup needs at least one Motor")
        self.motors = list(motors)
        _rt.register(self)

    def count(self):
        return len(self.motors)

    # actions fan out; blocking waits on the first motor
    def spin(self, direction, velocity=None, units=None):
        for m in self.motors:
            m.spin(direction, velocity, units)

    def spin_for(self, direction, angle, units=DEGREES, velocity=None,
                 units_v=None, wait=True):
        for m in self.motors:
            m.spin_for(direction, angle, units, velocity, units_v, wait=False)
        if wait:
            self.motors[0]._wait_done()
            if not self.motors[0]._done:
                self.stop()

    def spin_to_position(self, rotation, units=DEGREES, velocity=None,
                         units_v=None, wait=True):
        for m in self.motors:
            m.spin_to_position(rotation, units, velocity, units_v, wait=False)
        if wait:
            self.motors[0]._wait_done()
            if not self.motors[0]._done:
                self.stop()

    def stop(self, mode=None):
        for m in self.motors:
            m.stop(mode)

    def set_velocity(self, velocity, units=None):
        for m in self.motors:
            m.set_velocity(velocity, units)

    def set_max_torque(self, value, units=PERCENT):
        for m in self.motors:
            m.set_max_torque(value, units)

    def set_position(self, position, units=DEGREES):
        for m in self.motors:
            m.set_position(position, units)

    def reset_position(self):
        for m in self.motors:
            m.reset_position()

    def set_stopping(self, mode):
        for m in self.motors:
            m.set_stopping(mode)

    def set_timeout(self, value, units=MSEC):
        for m in self.motors:
            m.set_timeout(value, units)

    def position(self, units=DEGREES):
        return self.motors[0].position(units)

    def velocity(self, units=RPM):
        return self.motors[0].velocity(units)

    def current(self, units=CurrentUnits.AMP):
        return sum(m.current(units) for m in self.motors)

    def power(self):
        return sum(m.power() for m in self.motors)

    def torque(self, units=TorqueUnits.NM):
        return sum(m.torque(units) for m in self.motors)

    def efficiency(self):
        return self.motors[0].efficiency()

    def temperature(self, units=TemperatureUnits.CELSIUS):
        return self.motors[0].temperature(units)

    def is_done(self):
        return all(m.is_done() for m in self.motors)

    def is_spinning(self):
        return any(m.is_spinning() for m in self.motors)

    def direction(self):
        return self.motors[0].direction()


# ============================================================
# Inertial / Gyro
# ============================================================

class Inertial:
    """The IQ 2nd-gen Brain's built-in inertial sensor: Inertial() with no
    port. Heading is clockwise-positive, 0-359.99; rotation is cumulative
    (right turns +)."""

    def __init__(self, port=None):
        self.port = port
        self._heading_offset = 0.0
        self._rotation_offset = 0.0
        self._calibrating_until = -1.0
        _rt.register(self)

    # raw clockwise rotation from the physics world
    def _raw_cw(self):
        return _world().cw_rotation_deg()

    def calibrate(self):
        clock = _clock()
        self._calibrating_until = clock.now() + 1.5
        clock.sleep(1.5)  # docs: blocking; generated code also polls after

    def is_calibrating(self):
        return _clock().now() < self._calibrating_until

    def heading(self, units=DEGREES):
        h = _normalize_deg(self._raw_cw() + self._heading_offset)
        h += _world().heading_noise_deg()
        return _deg_to_rot(_normalize_deg(h), units)

    def rotation(self, units=DEGREES):
        return _deg_to_rot(self._raw_cw() + self._rotation_offset, units)

    def set_heading(self, value, units=DEGREES):
        self._heading_offset = _rot_to_deg(value, units) - self._raw_cw()

    def set_rotation(self, value, units=DEGREES):
        self._rotation_offset = _rot_to_deg(value, units) - self._raw_cw()

    def reset_heading(self):
        self.set_heading(0, DEGREES)

    def reset_rotation(self):
        self.set_rotation(0, DEGREES)

    def orientation(self, axis, units=DEGREES):
        if axis is YAW or axis is OrientationType.YAW:
            return self.heading(units)
        return 0.0  # flat field: roll and pitch are 0

    def gyro_rate(self, axis, units=DPS):
        if axis is ZAXIS:
            return -_world().omega_dps()  # clockwise-positive
        return 0.0

    def acceleration(self, axis):
        import random
        noise = random.uniform(-0.02, 0.02)
        if axis is ZAXIS:
            return 1.0 + noise  # gravity
        return noise

    def changed(self, callback, arg=()):
        _poll_changed(lambda: round(self.heading()), callback, arg)

    def installed(self):
        return True


class Gyro:
    """External IQ gyro sensor; heading behaves like the Inertial's."""

    def __init__(self, port):
        self.port = port
        self._inner = Inertial(port)

    def calibrate(self):
        self._inner.calibrate()

    def is_calibrating(self):
        return self._inner.is_calibrating()

    def installed(self):
        return True

    def heading(self, units=DEGREES):
        return self._inner.heading(units)

    def rotation(self, units=DEGREES):
        return self._inner.rotation(units)

    def rate(self, units=DPS):
        return self._inner.gyro_rate(ZAXIS, units)

    def set_heading(self, value, units=DEGREES):
        self._inner.set_heading(value, units)

    def set_rotation(self, value, units=DEGREES):
        self._inner.set_rotation(value, units)

    def reset_heading(self):
        self._inner.reset_heading()

    def reset_rotation(self):
        self._inner.reset_rotation()

    def changed(self, callback, arg=()):
        self._inner.changed(callback, arg)


# ============================================================
# DriveTrain / SmartDrive
# ============================================================

class _DriveCommand:
    __slots__ = ("kind", "sign", "cw_sign", "vel_pct", "remaining_in",
                 "remaining_deg", "target_cw", "target_is_rotation",
                 "done", "deadline")

    def __init__(self, kind, **kw):
        self.kind = kind
        self.sign = kw.get("sign", 1.0)            # + forward
        self.cw_sign = kw.get("cw_sign", 1.0)      # + clockwise (RIGHT)
        self.vel_pct = kw.get("vel_pct", 50.0)
        self.remaining_in = kw.get("remaining_in", 0.0)
        self.remaining_deg = kw.get("remaining_deg", 0.0)
        self.target_cw = kw.get("target_cw", 0.0)
        self.target_is_rotation = kw.get("target_is_rotation", False)
        self.done = False
        self.deadline = kw.get("deadline")


class DriveTrain:
    def __init__(self, lm, rm, wheelTravel=300, trackWidth=320, wheelBase=320,
                 units=MM, externalGearRatio=1.0):
        self.lm = lm
        self.rm = rm
        self.wheel_travel_in = _dist_to_inches(wheelTravel, units)
        self.track_width_in = _dist_to_inches(trackWidth, units)
        self.wheel_base_in = _dist_to_inches(wheelBase, units)
        self.gear_ratio = externalGearRatio
        self._gyro = None
        self._drive_vel_pct = 50.0
        self._turn_vel_pct = 50.0
        self._stopping = BRAKE
        self._timeout_s = None
        self._turn_threshold = 1.0
        self._turn_constant = 1.0
        self._cmd = None  # current _DriveCommand or None
        # odometry-based heading for plain DriveTrain (set_heading support)
        self._odo = Inertial()
        _rt.register(self)
        _rt.require_sim().attach_drivetrain(self)

    # -- helpers --

    def _heading_sensor(self):
        return self._gyro if self._gyro is not None else self._odo

    def _vel(self, velocity, units_v, default_pct):
        return abs(default_pct if velocity is None else _vel_to_pct(velocity, units_v))

    def _deadline(self):
        if self._timeout_s is None:
            return None
        return _clock().now() + self._timeout_s

    def _start(self, cmd, wait):
        self._cmd = cmd
        if wait:
            finished = _clock().wait_for(
                lambda: cmd.done,
                timeout=self._timeout_s)
            if not finished and self._cmd is cmd:
                self.stop()

    # -- actions --

    def drive(self, direction, velocity=None, units=PERCENT):
        sign = -1.0 if direction is REVERSE else 1.0
        self._cmd = _DriveCommand("drive", sign=sign,
                                  vel_pct=self._vel(velocity, units, self._drive_vel_pct))

    def drive_for(self, direction, distance, units=INCHES, velocity=None,
                  units_v=None, wait=True):
        sign = -1.0 if direction is REVERSE else 1.0
        cmd = _DriveCommand(
            "drive_for", sign=sign,
            remaining_in=abs(_dist_to_inches(distance, units)),
            # docs: units_v defaults to RPM for drive_for
            vel_pct=self._vel(velocity, units_v if units_v is not None else RPM,
                              self._drive_vel_pct),
            deadline=self._deadline())
        self._start(cmd, wait)

    def turn(self, direction, velocity=None, units=RPM):  # docs: turn defaults to RPM
        if direction is not LEFT and direction is not RIGHT:
            raise VexSimError(f"turn direction must be LEFT or RIGHT, got {direction!r}")
        cw = 1.0 if direction is RIGHT else -1.0
        self._cmd = _DriveCommand("turn", cw_sign=cw,
                                  vel_pct=self._vel(velocity, units, self._turn_vel_pct))

    def turn_for(self, direction, angle, units=DEGREES, velocity=None,
                 units_v=None, wait=True):
        if direction is not LEFT and direction is not RIGHT:
            raise VexSimError(f"turn direction must be LEFT or RIGHT, got {direction!r}")
        cw = 1.0 if direction is RIGHT else -1.0
        cmd = _DriveCommand(
            "turn_for", cw_sign=cw,
            remaining_deg=abs(_rot_to_deg(angle, units)),
            # docs: units_v defaults to RPM for turn_for (PERCENT for turn_to_*)
            vel_pct=self._vel(velocity, units_v if units_v is not None else RPM,
                              self._turn_vel_pct),
            deadline=self._deadline())
        self._start(cmd, wait)

    def turn_to_heading(self, angle, units=DEGREES, velocity=None,
                        units_v=None, wait=True):
        cmd = _DriveCommand(
            "turn_to", target_cw=_normalize_deg(_rot_to_deg(angle, units)),
            vel_pct=self._vel(velocity, units_v, self._turn_vel_pct),
            deadline=self._deadline())
        self._start(cmd, wait)

    def turn_to_rotation(self, angle, units=DEGREES, velocity=None,
                         units_v=None, wait=True):
        cmd = _DriveCommand(
            "turn_to", target_cw=_rot_to_deg(angle, units), target_is_rotation=True,
            vel_pct=self._vel(velocity, units_v, self._turn_vel_pct),
            deadline=self._deadline())
        self._start(cmd, wait)

    def stop(self, mode=None):
        self._cmd = None
        if mode is not None:
            self._stopping = mode

    # -- mutators --

    def set_drive_velocity(self, velocity, units=PERCENT):
        self._drive_vel_pct = _vel_to_pct(velocity, units)

    def set_turn_velocity(self, velocity, units=PERCENT):
        self._turn_vel_pct = _vel_to_pct(velocity, units)

    def set_stopping(self, mode):
        self._stopping = mode

    def set_timeout(self, value, units=MSEC):
        self._timeout_s = _time_to_s(value, units)

    def set_heading(self, heading, units=DEGREES):
        self._heading_sensor().set_heading(heading, units)

    def set_rotation(self, rotation, units=DEGREES):
        self._heading_sensor().set_rotation(rotation, units)

    def set_turn_threshold(self, value):
        self._turn_threshold = float(value)

    def set_turn_constant(self, value):
        self._turn_constant = float(value)

    # -- getters --

    def heading(self, units=DEGREES):
        return self._heading_sensor().heading(units)

    def rotation(self, units=DEGREES):
        return self._heading_sensor().rotation(units)

    def velocity(self, units=PERCENT):
        return (self.lm.velocity(units) + self.rm.velocity(units)) / 2.0

    def current(self, units=CurrentUnits.AMP):
        return self.lm.current(units) + self.rm.current(units)

    def power(self):
        return self.lm.power() + self.rm.power()

    def torque(self, units=TorqueUnits.NM):
        return self.lm.torque(units) + self.rm.torque(units)

    def efficiency(self):
        return self.lm.efficiency()

    def temperature(self, units=TemperatureUnits.CELSIUS):
        return self.lm.temperature(units)

    def is_moving(self):
        return self._cmd is not None and not self._cmd.done

    def is_done(self):
        return not self.is_moving()

    def is_turning(self):
        return (self._cmd is not None and not self._cmd.done
                and self._cmd.kind in ("turn", "turn_for", "turn_to"))


class SmartDrive(DriveTrain):
    def __init__(self, lm, rm, g, wheelTravel=300, trackWidth=320,
                 wheelBase=320, units=MM, externalGearRatio=1.0):
        super().__init__(lm, rm, wheelTravel, trackWidth, wheelBase, units,
                         externalGearRatio)
        self._gyro = g


# ============================================================
# Brain
# ============================================================

class _BrainButton:
    def __init__(self, name):
        self.name = name
        self._watch = _PressWatcher(self.pressing)

    def pressing(self):
        return _world().brain_button_pressing(self.name)

    def pressed(self, callback, arg=()):
        self._watch.on_pressed(callback, arg)

    def released(self, callback, arg=()):
        self._watch.on_released(callback, arg)


class _Battery:
    def capacity(self):
        return 100

    def voltage(self, units=MV):
        return 8000.0 if units is MV else 8.0

    def current(self):
        return 0.5


class _Screen:
    """Models the 160x108 IQ2 screen. Text and drawing ops are recorded and
    rendered in the simulator's side panel."""

    COLS = 26
    ROWS = 9

    def __init__(self):
        self._lock = threading.Lock()
        self._rows = [""] * self.ROWS
        self._row = 1
        self._col = 1
        self._pen = Color.WHITE
        self._fill = Color.BLACK
        self._draws = []  # list of ("pixel"|"line"|"rect"|"circle"|"text", ...)
        self._font = FontType.MONO12

    # ---- text cursor API ----

    def _fmt(self, args, precision):
        parts = []
        for a in args:
            if isinstance(a, float):
                parts.append(f"{a:.{precision}f}")
            else:
                parts.append(str(a))
        return " ".join(parts)

    def print(self, *args, precision=2, opaque=False, sep=" "):
        text = self._fmt(args, precision)
        with self._lock:
            r = min(max(self._row, 1), self.ROWS) - 1
            line = self._rows[r]
            col = self._col - 1
            if len(line) < col:
                line = line.ljust(col)
            self._rows[r] = (line[:col] + text)[:self.COLS + 10]
            self._col += len(text)
        print(f"[brain] {text}")

    def set_cursor(self, row, column):
        with self._lock:
            self._row = int(row)
            self._col = int(column)

    def next_row(self):
        with self._lock:
            self._row += 1
            self._col = 1

    def new_line(self):  # undocumented but used in real programs
        self.next_row()

    def clear_row(self, row=None, color=None):
        with self._lock:
            r = (self._row if row is None else int(row)) - 1
            if 0 <= r < self.ROWS:
                self._rows[r] = ""

    def clear_screen(self, color=None):
        with self._lock:
            self._rows = [""] * self.ROWS
            self._draws.clear()
            self._row = 1
            self._col = 1

    def row(self):
        return self._row

    def column(self):
        return self._col

    # ---- pixel API ----

    def print_at(self, *args, x=0, y=0, precision=2, opaque=False):
        text = self._fmt(args, precision)
        with self._lock:
            self._draws.append(("text", x, y, text, self._pen))

    def get_string_width(self, string):
        return len(str(string)) * 6

    def get_string_height(self, string):
        return 12

    def set_font(self, fontname):
        self._font = fontname
        if fontname is not FontType.MONO12:
            _rt.note_once("font", "the sim panel renders all fonts at one size; "
                                  "row/column counts assume MONO12")

    def set_pen_width(self, width):
        _rt.note_once("pen_width", "set_pen_width is recorded but the sim panel draws 1px lines")

    def set_pen_color(self, color=None):
        self._pen = color or Color.WHITE

    def set_fill_color(self, color=None):
        self._fill = color or Color.BLACK

    def set_origin(self, x, y):
        raise VexSimNotImplemented("brain.screen.set_origin")

    def set_clip_region(self, x, y, width, height):
        raise VexSimNotImplemented("brain.screen.set_clip_region")

    def draw_pixel(self, x, y):
        with self._lock:
            self._draws.append(("pixel", x, y, None, self._pen))

    def draw_line(self, x1, y1, x2, y2):
        with self._lock:
            self._draws.append(("line", x1, y1, (x2, y2), self._pen))

    def draw_rectangle(self, x, y, width, height, color=None):
        with self._lock:
            self._draws.append(("rect", x, y, (width, height), color or self._fill))

    def draw_circle(self, x, y, radius, color=None):
        with self._lock:
            self._draws.append(("circle", x, y, radius, color or self._fill))

    def render(self):
        pass  # the sim panel always renders live

    # ---- renderer access ----

    def snapshot(self):
        with self._lock:
            return list(self._rows), list(self._draws)


class Brain:
    def __init__(self):
        self.screen = _Screen()
        self.timer = Timer()
        self.battery = _Battery()
        self.buttonLeft = _BrainButton("left")
        self.buttonCheck = _BrainButton("check")
        self.buttonRight = _BrainButton("right")
        _rt.register(self)
        _rt.require_sim().attach_brain(self)

    def play_sound(self, sound):
        print(f"[brain] (sound) {sound}")

    def play_note(self, octave, note, duration=500):
        print(f"[brain] (note) octave={octave} note={note} {duration}ms")
        _clock().sleep(duration / 1000.0)

    def sound_off(self):
        pass

    def program_stop(self):
        _world().request_program_stop()
        raise SystemExit(0)


# ============================================================
# Sensors
# ============================================================

class Distance:
    """2nd-gen Distance sensor, simulated by raycasting against the field.

    Sees: perimeter, yellow walls, pyramids, posts, octagons.
    Does not see: bean bags, floor barriers (too low)."""

    def __init__(self, port):
        self.port = port
        _rt.register(self)

    def _raw_mm(self):
        return _world().distance_raycast_mm()

    def is_object_detected(self):
        return self._raw_mm() is not None

    def object_distance(self, units=MM):
        mm = self._raw_mm()
        if mm is None:
            # real out-of-range behavior is undocumented; we return the max
            mm = _rt.config.robot.dist_max_range_mm
        return _inches_to_dist(mm / _MM_PER_IN, units)

    def object_velocity(self):
        return _world().distance_closing_mps()

    def object_size(self):
        if not self.is_object_detected():
            return ObjectSizeType.NONE
        return ObjectSizeType.MEDIUM

    def installed(self):
        return True

    def changed(self, callback, arg=()):
        _poll_changed(lambda: round(self.object_distance(MM) / 10.0), callback, arg)


class Bumper:
    """Bumper switch. The sim presses it when the robot is pushing against
    an obstacle in the bumper's direction (front by default)."""

    def __init__(self, port):
        self.port = port
        self._watch = _PressWatcher(self.pressing)
        _rt.register(self)

    def pressing(self):
        return 1 if _world().bumper_pressing() else 0

    def pressed(self, callback, arg=()):
        self._watch.on_pressed(callback, arg)

    def released(self, callback, arg=()):
        self._watch.on_released(callback, arg)


class Touchled:
    _count = 0

    def __init__(self, port):
        self.port = port
        self.color_rgb = None       # rendered in the HUD
        self.brightness = 100
        self.index = Touchled._count  # which keyboard key presses it
        Touchled._count += 1
        self._watch = _PressWatcher(self.pressing)
        _rt.register(self)

    def _set(self, color):
        rgb = getattr(color, "_rgb", None)
        if rgb is None:
            raise VexSimError(f"not a Color: {color!r}")
        self.color_rgb = rgb

    def on(self, value=Color.WHITE):
        self.brightness = 100
        self._set(value)

    def off(self):
        self.brightness = 0
        self.color_rgb = None

    def toggle(self):
        if self.color_rgb is None:
            self.on()
        else:
            self.off()

    def set_color(self, color=Color.WHITE):
        if self.brightness == 0:
            self.brightness = 100
        self._set(color)

    def set_brightness(self, brightness):
        self.brightness = int(brightness)

    def set_fade(self, type):
        pass  # cosmetic only

    def set_blink(self, color, ontime=0.25, offtime=0.25):
        self._set(color)
        _rt.note_once("blink", "set_blink shows a steady color in the sim panel")

    def pressing(self):
        return 1 if _world().touchled_pressing(self.index) else 0

    def pressed(self, callback, arg=()):
        self._watch.on_pressed(callback, arg)

    def released(self, callback, arg=()):
        self._watch.on_released(callback, arg)

    def installed(self):
        return True


class Optical:
    """Optical sensor, assumed front-mounted: reports the color of a bean
    bag directly in front of the robot."""

    def __init__(self, port):
        self.port = port
        _rt.register(self)

    def _bag_color(self):
        return _world().bag_color_in_front()  # "red"|"blue"|"yellow"|None

    def set_light(self, state):
        pass

    def set_light_power(self, value):
        pass

    def object_detect_threshold(self, value):
        return value

    def is_near_object(self):
        return self._bag_color() is not None

    def color(self):
        c = self._bag_color()
        if c == "red":
            return Color.RED
        if c == "blue":
            return Color.BLUE
        if c == "yellow":
            return Color.YELLOW
        return Color.BLACK

    def brightness(self, readraw=False):
        return 50.0

    def hue(self):
        c = self._bag_color()
        return {"red": 0.0, "yellow": 60.0, "blue": 220.0}.get(c, 0.0)

    def rgb(self, raw=False):
        c = self.color()
        r, g, b = c._rgb
        return (r, g, b, 50)

    def installed(self):
        return True

    def object_detected(self, callback, arg=()):
        watch = _PressWatcher(self.is_near_object)
        watch.on_pressed(callback, arg)

    def object_lost(self, callback, arg=()):
        watch = _PressWatcher(self.is_near_object)
        watch.on_released(callback, arg)


class ColorSensor:
    def __init__(self, port):
        raise VexSimNotImplemented(
            "ColorSensor (1st-gen)",
            "Use Optical(port) instead; it is the 2nd-gen equivalent and is simulated.")


class Pneumatic:
    def __init__(self, port):
        raise VexSimNotImplemented(
            "Pneumatic", "The simulator does not model pneumatics (v1).")


class Vision:
    def __init__(self, *a, **k):
        raise VexSimNotImplemented("Vision sensor")


class AiVision:
    def __init__(self, *a, **k):
        raise VexSimNotImplemented(
            "AI Vision sensor",
            "Use the Distance sensor or Optical sensor in the sim for now.")


class Sonar:
    def __init__(self, port):
        raise VexSimNotImplemented(
            "Sonar (1st-gen distance)", "Use Distance(port) instead.")


# ============================================================
# Controller (keyboard-driven)
# ============================================================

class _ControllerAxis:
    def __init__(self, name):
        self.name = name

    def position(self):
        return _world().controller_axis(self.name)

    def changed(self, callback, arg=()):
        _poll_changed(lambda: self.position() // 10, callback, arg)


class _ControllerButton:
    def __init__(self, name):
        self.name = name
        self._watch = _PressWatcher(self.pressing)

    def pressing(self):
        return _world().controller_button(self.name)

    def pressed(self, callback, arg=()):
        self._watch.on_pressed(callback, arg)

    def released(self, callback, arg=()):
        self._watch.on_released(callback, arg)


class Controller:
    """Driven from the keyboard while the sim window has focus — see the
    README key map (WASD = left stick, arrows = right stick, etc.)."""

    def __init__(self):
        self.axisA = _ControllerAxis("A")  # left stick vertical
        self.axisB = _ControllerAxis("B")  # left stick horizontal
        self.axisC = _ControllerAxis("C")  # right stick horizontal
        self.axisD = _ControllerAxis("D")  # right stick vertical
        for name in ("EUp", "EDown", "FUp", "FDown",
                     "LUp", "LDown", "RUp", "RDown", "L3", "R3"):
            setattr(self, "button" + name, _ControllerButton(name))
        self.remote_control_code_enabled = True
        _rt.register(self)

    def rumble(self, *a, **k):
        raise VexSimNotImplemented("controller.rumble")


# ============================================================
# Console helpers
# ============================================================

def clear_console():
    print("\n" + "-" * 40)


def set_console_text_color(color):
    pass  # terminal colors not modeled


MAX_PORTS = 12
