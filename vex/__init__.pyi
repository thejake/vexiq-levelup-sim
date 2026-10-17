"""Type stubs for the simulated VEX IQ 2nd-gen Python API.

These make autocomplete and hover-help work in VS Code: the real module
builds its enums dynamically at runtime, which type checkers can't see
through. Docstrings are written for the simulator, in our own words.
Keep in sync with vex/__init__.py.
"""

from typing import Any, Callable, Iterable

# ============================================================
# Enums and constants
# ============================================================

class vexEnum:
    value: int
    name: str

class PercentUnits:
    class PercentUnits(vexEnum): ...
    PERCENT: PercentUnits

class TimeUnits:
    class TimeUnits(vexEnum): ...
    SECONDS: TimeUnits
    MSEC: TimeUnits

class DistanceUnits:
    class DistanceUnits(vexEnum): ...
    MM: DistanceUnits
    IN: DistanceUnits
    CM: DistanceUnits

class RotationUnits:
    class RotationUnits(vexEnum): ...
    DEG: RotationUnits
    REV: RotationUnits
    RAW: RotationUnits

class VelocityUnits:
    class VelocityUnits(vexEnum): ...
    PCT: VelocityUnits
    RPM: VelocityUnits
    DPS: VelocityUnits

class TorqueUnits:
    class TorqueUnits(vexEnum): ...
    NM: TorqueUnits
    INLB: TorqueUnits

class CurrentUnits:
    class CurrentUnits(vexEnum): ...
    AMP: CurrentUnits

class PowerUnits:
    class PowerUnits(vexEnum): ...
    WATT: PowerUnits

class TemperatureUnits:
    class TemperatureUnits(vexEnum): ...
    CELSIUS: TemperatureUnits
    FAHRENHEIT: TemperatureUnits

class VoltageUnits:
    class VoltageUnits(vexEnum): ...
    VOLT: VoltageUnits
    MV: VoltageUnits

class DirectionType:
    class DirectionType(vexEnum): ...
    FORWARD: DirectionType
    REVERSE: DirectionType

class TurnType:
    class TurnType(vexEnum): ...
    LEFT: TurnType
    RIGHT: TurnType

class BrakeType:
    class BrakeType(vexEnum): ...
    COAST: BrakeType
    BRAKE: BrakeType
    HOLD: BrakeType

class AxisType:
    class AxisType(vexEnum): ...
    XAXIS: AxisType
    YAXIS: AxisType
    ZAXIS: AxisType

class OrientationType:
    class OrientationType(vexEnum): ...
    ROLL: OrientationType
    PITCH: OrientationType
    YAW: OrientationType

class ObjectSizeType:
    class ObjectSizeType(vexEnum): ...
    NONE: ObjectSizeType
    SMALL: ObjectSizeType
    MEDIUM: ObjectSizeType
    LARGE: ObjectSizeType

class LedStateType:
    class LedStateType(vexEnum): ...
    OFF: LedStateType
    ON: LedStateType
    BLINK: LedStateType

class FadeType:
    class FadeType(vexEnum): ...
    OFF: FadeType
    SLOW: FadeType
    FAST: FadeType

class GearSetting:
    class GearSetting(vexEnum): ...
    RATIO_1_1: GearSetting
    RATIO_2_1: GearSetting
    RATIO_3_1: GearSetting

class FontType:
    class FontType(vexEnum): ...
    MONO12: FontType
    MONO15: FontType
    MONO20: FontType
    MONO30: FontType
    MONO40: FontType
    MONO60: FontType
    PROP20: FontType
    PROP30: FontType
    PROP40: FontType
    PROP60: FontType

class SoundType:
    class SoundType(vexEnum): ...
    SIREN: SoundType
    WRONG_WAY: SoundType
    WRONG_WAY_SLOW: SoundType
    FILLUP: SoundType
    HEADLIGHTS_ON: SoundType
    HEADLIGHTS_OFF: SoundType
    TOLLBOOTH: SoundType
    ALARM: SoundType
    TADA: SoundType
    DOOR_CLOSE: SoundType
    RATCHET: SoundType
    WRENCH: SoundType
    SIREN2: SoundType
    RATCHET2: SoundType
    ALARM2: SoundType
    POWER_DOWN: SoundType

class CylinderType:
    class CylinderType(vexEnum): ...
    CYLINDER1: CylinderType
    CYLINDER2: CylinderType
    CYLINDERALL: CylinderType

# Bare constants (what VEXcode programs actually use)
PERCENT: PercentUnits.PercentUnits
SECONDS: TimeUnits.TimeUnits
MSEC: TimeUnits.TimeUnits
MM: DistanceUnits.DistanceUnits
INCHES: DistanceUnits.DistanceUnits
DEGREES: RotationUnits.RotationUnits
TURNS: RotationUnits.RotationUnits
RPM: VelocityUnits.VelocityUnits
DPS: VelocityUnits.VelocityUnits
AMP: CurrentUnits.CurrentUnits
VOLT: VoltageUnits.VoltageUnits
MV: VoltageUnits.VoltageUnits
FORWARD: DirectionType.DirectionType
REVERSE: DirectionType.DirectionType
LEFT: TurnType.TurnType
RIGHT: TurnType.TurnType
COAST: BrakeType.BrakeType
BRAKE: BrakeType.BrakeType
HOLD: BrakeType.BrakeType
XAXIS: AxisType.AxisType
YAXIS: AxisType.AxisType
ZAXIS: AxisType.AxisType
ROLL: OrientationType.OrientationType
PITCH: OrientationType.OrientationType
YAW: OrientationType.OrientationType
CYLINDER1: CylinderType.CylinderType
CYLINDER2: CylinderType.CylinderType
CYLINDERALL: CylinderType.CylinderType

class Ports:
    """The 12 Smart Ports on the Brain. Use like: Motor(Ports.PORT1)."""
    PORT1: int
    PORT2: int
    PORT3: int
    PORT4: int
    PORT5: int
    PORT6: int
    PORT7: int
    PORT8: int
    PORT9: int
    PORT10: int
    PORT11: int
    PORT12: int

PORT1: int
PORT2: int
PORT3: int
PORT4: int
PORT5: int
PORT6: int
PORT7: int
PORT8: int
PORT9: int
PORT10: int
PORT11: int
PORT12: int

MAX_PORTS: int

class Color:
    """A color. Use the predefined ones (Color.RED, Color.BLUE, ...) or
    make your own: Color(0x00FF00), Color("#00FF00"), or Color(r, g, b)."""

    class DefinedColor:
        name: str

    BLACK: DefinedColor
    WHITE: DefinedColor
    RED: DefinedColor
    GREEN: DefinedColor
    BLUE: DefinedColor
    YELLOW: DefinedColor
    ORANGE: DefinedColor
    PURPLE: DefinedColor
    CYAN: DefinedColor
    TRANSPARENT: DefinedColor
    RED_VIOLET: DefinedColor
    VIOLET: DefinedColor
    BLUE_VIOLET: DefinedColor
    BLUE_GREEN: DefinedColor
    YELLOW_GREEN: DefinedColor
    YELLOW_ORANGE: DefinedColor
    RED_ORANGE: DefinedColor

    def __init__(self, *args: Any) -> None:
        """Color(0xRRGGBB), Color("#RRGGBB"), or Color(r, g, b) with 0-255 each."""
    def rgb(self, r: int, g: int, b: int) -> None:
        """Change this color's red/green/blue values (0-255 each)."""
    def hsv(self, h: float, s: float, v: float) -> None:
        """Change this color by hue (0-359), saturation and value (0.0-1.0)."""
    def web(self, value: str) -> None:
        """Change this color using a web string like "#AA2896"."""

_AnyColor = Color | Color.DefinedColor

# ============================================================
# Timing, events, threads
# ============================================================

def wait(time: float, units: TimeUnits.TimeUnits = ...) -> None:
    """Pause this part of your program for an amount of time.

    Careful: units default to MSEC, so wait(2) is 2 *milliseconds*.
    Write wait(2, SECONDS) or wait(2000, MSEC) for 2 seconds.
    In the simulator this waits in SIM time, so pausing the sim or
    changing its speed affects your waits too."""

def sleep(time: float, units: TimeUnits.TimeUnits = ...) -> None:
    """Same as wait(). VEXcode's auto-generated code uses this name."""

class Thread:
    """Runs a function at the same time as the rest of your program.

    Example:
        def blink_forever():
            while True:
                led.toggle()
                wait(500, MSEC)
        Thread(blink_forever)   # starts immediately
    """
    def __init__(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Start running `callback` in parallel, right now."""
    def stop(self) -> None:
        """Not supported in the simulator — have your function check a
        variable and return instead."""

class Event:
    """Lets one part of your program signal another. Register functions on
    the event, then broadcast() runs them all at once.

    Example:
        scored = Event()
        scored(celebrate)        # register a function
        scored.broadcast()       # runs celebrate() in parallel
    """
    def __init__(self, callback: Callable[..., Any] | None = ..., args: tuple[Any, ...] = ...) -> None: ...
    def __call__(self, callback: Callable[..., Any], args: tuple[Any, ...] = ...) -> None:
        """Register another function to run when this event broadcasts."""
    def set(self, callback: Callable[..., Any], args: tuple[Any, ...] = ...) -> None:
        """Register another function to run when this event broadcasts."""
    def broadcast(self) -> None:
        """Start every registered function, each in parallel. Doesn't wait."""
    def broadcast_and_wait(self) -> None:
        """Start every registered function and wait until they all finish."""

class Timer:
    """A stopwatch. Starts counting the moment you create it.
    The Brain already has one running: brain.timer."""
    def __init__(self) -> None: ...
    def time(self, units: TimeUnits.TimeUnits = ...) -> float:
        """How long since this timer started (or was last cleared).
        Units default to MSEC; use time(SECONDS) for seconds."""
    def clear(self) -> None:
        """Reset this timer back to zero."""
    def system(self) -> float:
        """Milliseconds since the program started."""
    def system_high_res(self) -> float:
        """Microseconds since the program started."""
    def event(self, callback: Callable[..., Any], delay: float, arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` once, `delay` milliseconds from now."""

# ============================================================
# Motors
# ============================================================

class Motor:
    """One IQ Smart Motor. In the simulator, motors on your drivetrain move
    the robot; the motor on the intake port (see simconfig.toml) grabs and
    ejects bean bags; any other motor just tracks its spin and position."""

    port: int
    gear_ratio: float
    reversed: bool

    def __init__(self, port: int, *args: Any, **kwargs: Any) -> None:
        """Motor(port), Motor(port, reverse), or Motor(port, gear_ratio, reverse).

        `reverse=True` flips which way FORWARD spins — used so that both
        drive motors move the robot forward together. VEXcode generates
        these lines for you in the robot-config block."""
    def spin(self, direction: DirectionType.DirectionType, velocity: float | None = ...,
             units: vexEnum | None = ...) -> None:
        """Start spinning and keep spinning until another command or stop().
        Doesn't wait — your program continues immediately.
        Speed comes from set_velocity() unless you pass one here."""
    def spin_for(self, direction: DirectionType.DirectionType, angle: float,
                 units: RotationUnits.RotationUnits = ..., velocity: float | None = ...,
                 units_v: vexEnum | None = ..., wait: bool = ...) -> None:
        """Spin by an amount from where it is now, e.g. spin_for(FORWARD, 90, DEGREES).

        Blocks until the move finishes (or the set_timeout limit hits).
        Pass wait=False to continue immediately and check is_done() later."""
    def spin_to_position(self, rotation: float, units: RotationUnits.RotationUnits = ...,
                         velocity: float | None = ..., units_v: vexEnum | None = ...,
                         wait: bool = ...) -> None:
        """Spin to an absolute position on the motor's own position counter
        (see position / set_position). Good for arms: 0 = down, 300 = up.
        Blocks unless wait=False."""
    def stop(self, mode: BrakeType.BrakeType | None = ...) -> None:
        """Stop the motor. Optional mode: COAST rolls free, BRAKE stops,
        HOLD actively holds the position."""
    def set_velocity(self, velocity: float, units: vexEnum | None = ...) -> None:
        """Set the speed later spin commands use, e.g. set_velocity(75, PERCENT).
        Changing it during spin() changes the ongoing spin; a negative value
        reverses it."""
    def set_max_torque(self, value: float, units: vexEnum = ...) -> None:
        """Limit how hard the motor pushes. Recorded but has no effect in
        the simulator (there is no stall model)."""
    def set_position(self, position: float, units: RotationUnits.RotationUnits = ...) -> None:
        """Renumber the position counter: the motor's CURRENT position now
        reads as this value. Doesn't move anything."""
    def reset_position(self) -> None:
        """Make the current position read as 0. Doesn't move anything."""
    def set_stopping(self, mode: BrakeType.BrakeType) -> None:
        """What stop() does from now on: COAST, BRAKE, or HOLD."""
    def set_timeout(self, value: float, units: TimeUnits.TimeUnits = ...) -> None:
        """Give up on a blocked spin_for/spin_to_position after this long,
        instead of pushing forever. Set this on anything that can jam."""
    def get_timeout(self) -> float:
        """The current timeout in milliseconds (0 = none)."""
    def set_reversed(self, value: bool) -> None:
        """Flip which way FORWARD spins."""
    def position(self, units: RotationUnits.RotationUnits = ...) -> float:
        """How far the motor has turned, in DEGREES (default) or TURNS.
        Keeps counting up/down forever — it does not wrap at 360."""
    def velocity(self, units: vexEnum = ...) -> float:
        """Current speed. Default units are RPM (not percent!); positive
        means spinning forward."""
    def current(self, units: CurrentUnits.CurrentUnits = ...) -> float:
        """Motor current in amps (a rough fake value in the simulator)."""
    def power(self) -> float:
        """Motor power in watts (a rough fake value in the simulator)."""
    def torque(self, units: TorqueUnits.TorqueUnits = ...) -> float:
        """Motor torque (always 0 in the simulator — no load model)."""
    def efficiency(self) -> float:
        """Percent efficiency (a rough fake value in the simulator)."""
    def temperature(self, units: TemperatureUnits.TemperatureUnits = ...) -> float:
        """Motor temperature (always cool in the simulator)."""
    def is_done(self) -> bool:
        """True when the last spin_for/spin_to_position has finished.
        Use with wait=False: while not motor.is_done(): wait(20, MSEC)"""
    def is_spinning(self) -> bool:
        """True while the motor is running a command."""
    def direction(self) -> DirectionType.DirectionType:
        """FORWARD or REVERSE, whichever way it's currently spinning."""
    def installed(self) -> bool:
        """True if the motor is plugged in (always True in the simulator)."""

class MotorGroup:
    """Several motors driven as one — same commands as Motor, sent to all
    of them. Example: intake = MotorGroup(intake_a, intake_b)."""

    motors: list[Motor]
    def __init__(self, *motors: Motor) -> None: ...
    def count(self) -> int:
        """How many motors are in the group."""
    def spin(self, direction: DirectionType.DirectionType, velocity: float | None = ...,
             units: vexEnum | None = ...) -> None:
        """Start all motors spinning until another command. Doesn't wait."""
    def spin_for(self, direction: DirectionType.DirectionType, angle: float,
                 units: RotationUnits.RotationUnits = ..., velocity: float | None = ...,
                 units_v: vexEnum | None = ..., wait: bool = ...) -> None:
        """Spin all motors by an amount. Blocks unless wait=False."""
    def spin_to_position(self, rotation: float, units: RotationUnits.RotationUnits = ...,
                         velocity: float | None = ..., units_v: vexEnum | None = ...,
                         wait: bool = ...) -> None:
        """Spin all motors to an absolute position. Blocks unless wait=False."""
    def stop(self, mode: BrakeType.BrakeType | None = ...) -> None:
        """Stop all motors in the group."""
    def set_velocity(self, velocity: float, units: vexEnum | None = ...) -> None:
        """Set the speed later spin commands use, for every motor."""
    def set_max_torque(self, value: float, units: vexEnum = ...) -> None:
        """Limit torque for every motor (no effect in the simulator)."""
    def set_position(self, position: float, units: RotationUnits.RotationUnits = ...) -> None:
        """Renumber every motor's position counter. Doesn't move anything."""
    def reset_position(self) -> None:
        """Make every motor's current position read as 0."""
    def set_stopping(self, mode: BrakeType.BrakeType) -> None:
        """What stop() does from now on: COAST, BRAKE, or HOLD."""
    def set_timeout(self, value: float, units: TimeUnits.TimeUnits = ...) -> None:
        """Give up on blocked moves after this long."""
    def position(self, units: RotationUnits.RotationUnits = ...) -> float:
        """Position of the first motor in the group."""
    def velocity(self, units: vexEnum = ...) -> float:
        """Speed of the first motor in the group (RPM by default)."""
    def current(self, units: CurrentUnits.CurrentUnits = ...) -> float: ...
    def power(self) -> float: ...
    def torque(self, units: TorqueUnits.TorqueUnits = ...) -> float: ...
    def efficiency(self) -> float: ...
    def temperature(self, units: TemperatureUnits.TemperatureUnits = ...) -> float: ...
    def is_done(self) -> bool:
        """True when every motor has finished its last move."""
    def is_spinning(self) -> bool:
        """True while any motor in the group is running a command."""
    def direction(self) -> DirectionType.DirectionType: ...

# ============================================================
# Inertial / Gyro
# ============================================================

class Inertial:
    """The gyro built into the IQ 2nd-gen Brain: it knows which way the
    robot is pointing. Inertial() with no port = the built-in one; VEXcode
    names it brain_inertial. In the simulator it reads the virtual robot's
    true direction (plus noise, if you turn that on in simconfig.toml).

    Two ways to read direction:
    - heading(): like a compass, 0-359.9, wraps around. Turning right
      increases it.
    - rotation(): a running total that never wraps. Three full right
      spins = 1080. Left turns subtract."""

    port: int | None
    def __init__(self, port: int | None = ...) -> None: ...
    def calibrate(self) -> None:
        """Measure the sensor's zero point. Takes about 1.5 seconds and the
        robot must hold still. Do this once at program start, before any
        turns (VEXcode's generated calibrate_drivetrain() does it)."""
    def is_calibrating(self) -> bool:
        """True while calibrate() is still working."""
    def heading(self, units: RotationUnits.RotationUnits = ...) -> float:
        """Which way the robot points, 0-359.9 like a compass. 0 is wherever
        it pointed at calibration (or what you set with set_heading).
        Turning right (clockwise) increases it; it wraps past 359."""
    def rotation(self, units: RotationUnits.RotationUnits = ...) -> float:
        """Total turning since start: right turns add, left turns subtract,
        and it keeps going past 360 (or below 0) without wrapping."""
    def set_heading(self, value: float, units: RotationUnits.RotationUnits = ...) -> None:
        """Renumber the compass: the direction the robot faces RIGHT NOW
        becomes this heading value. The robot doesn't move. Example:
        set_heading(0) makes 'here' the new zero direction."""
    def set_rotation(self, value: float, units: RotationUnits.RotationUnits = ...) -> None:
        """Renumber the running total: rotation() reads this value right
        now and counts on from there. The robot doesn't move."""
    def reset_heading(self) -> None:
        """Same as set_heading(0): current direction becomes heading 0."""
    def reset_rotation(self) -> None:
        """Same as set_rotation(0): the running total restarts at 0."""
    def orientation(self, axis: OrientationType.OrientationType,
                    units: RotationUnits.RotationUnits = ...) -> float:
        """Tilt angle on an axis (ROLL, PITCH, YAW). The simulated field is
        flat, so roll and pitch are always 0; YAW equals heading()."""
    def gyro_rate(self, axis: AxisType.AxisType, units: vexEnum = ...) -> float:
        """How fast the robot is rotating right now, in degrees/second."""
    def acceleration(self, axis: AxisType.AxisType) -> float:
        """Acceleration in G on an axis. On a flat field ZAXIS reads ~1.0
        (gravity); the others are ~0 plus a little noise."""
    def changed(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` whenever the heading changes."""
    def installed(self) -> bool: ...

class Gyro:
    """The external plug-in gyro sensor. Same idea as Inertial: heading()
    wraps 0-359.9, rotation() is a running total (right +, left -)."""
    port: int
    def __init__(self, port: int) -> None: ...
    def calibrate(self) -> None:
        """Measure the zero point (~1.5s, hold still)."""
    def is_calibrating(self) -> bool:
        """True while calibrate() is still working."""
    def installed(self) -> bool: ...
    def heading(self, units: RotationUnits.RotationUnits = ...) -> float:
        """Compass direction 0-359.9; right turns increase it; wraps."""
    def rotation(self, units: RotationUnits.RotationUnits = ...) -> float:
        """Running total of turning; right +, left -; never wraps."""
    def rate(self, units: vexEnum = ...) -> float:
        """How fast the robot is rotating right now (degrees/second)."""
    def set_heading(self, value: float, units: RotationUnits.RotationUnits = ...) -> None:
        """The current direction becomes this heading number. No movement."""
    def set_rotation(self, value: float, units: RotationUnits.RotationUnits = ...) -> None:
        """rotation() reads this value right now and counts on from there."""
    def reset_heading(self) -> None:
        """Same as set_heading(0)."""
    def reset_rotation(self) -> None:
        """Same as set_rotation(0)."""
    def changed(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` whenever the heading changes."""

# ============================================================
# Drivetrain
# ============================================================

class DriveTrain:
    """Drives the robot using the left and right motors together.
    This is the plain version with no gyro; SmartDrive (with the inertial)
    is what VEXcode normally generates and turns more accurately."""

    def __init__(self, lm: Motor | MotorGroup, rm: Motor | MotorGroup,
                 wheelTravel: float = ..., trackWidth: float = ...,
                 wheelBase: float = ..., units: DistanceUnits.DistanceUnits = ...,
                 externalGearRatio: float = ...) -> None:
        """lm/rm: left and right drive motors. wheelTravel: how far the
        robot rolls per wheel turn (an IQ 200mm wheel = 200). trackWidth:
        distance between left and right wheels — matters for turning."""
    def drive(self, direction: DirectionType.DirectionType, velocity: float | None = ...,
              units: vexEnum = ...) -> None:
        """Start driving and KEEP driving until stop() or another command.
        Doesn't wait. Pair it with a sensor loop:
            drivetrain.drive(FORWARD)
            while distance_front.object_distance(MM) > 300:
                wait(20, MSEC)
            drivetrain.stop()"""
    def drive_for(self, direction: DirectionType.DirectionType, distance: float,
                  units: DistanceUnits.DistanceUnits = ..., velocity: float | None = ...,
                  units_v: vexEnum | None = ..., wait: bool = ...) -> None:
        """Drive a set distance, then stop. CAREFUL: units default to
        INCHES — write drive_for(FORWARD, 300, MM) to be safe.
        Blocks until done; if the robot hits something it pushes until the
        set_timeout limit, so set a timeout! wait=False returns right away
        (check is_done() / is_moving() yourself)."""
    def turn(self, direction: TurnType.TurnType, velocity: float | None = ...,
             units: vexEnum = ...) -> None:
        """Start spinning in place (LEFT or RIGHT) and keep going until
        stop() or another command. Doesn't wait."""
    def turn_for(self, direction: TurnType.TurnType, angle: float,
                 units: RotationUnits.RotationUnits = ..., velocity: float | None = ...,
                 units_v: vexEnum | None = ..., wait: bool = ...) -> None:
        """Turn by an angle from where you are now, e.g.
        turn_for(RIGHT, 90, DEGREES). Blocks unless wait=False."""
    def turn_to_heading(self, angle: float, units: RotationUnits.RotationUnits = ...,
                        velocity: float | None = ..., units_v: vexEnum | None = ...,
                        wait: bool = ...) -> None:
        """Turn until the robot FACES a compass heading (0-359), taking the
        shortest way around. turn_to_heading(90) means "face heading 90"
        no matter where you point now. Blocks unless wait=False."""
    def turn_to_rotation(self, angle: float, units: RotationUnits.RotationUnits = ...,
                         velocity: float | None = ..., units_v: vexEnum | None = ...,
                         wait: bool = ...) -> None:
        """Turn until rotation() (the running total) reads this value.
        Unlike turn_to_heading this can wind up multiple full spins."""
    def stop(self, mode: BrakeType.BrakeType | None = ...) -> None:
        """Stop driving. Optional mode: COAST, BRAKE, or HOLD."""
    def set_drive_velocity(self, velocity: float, units: vexEnum = ...) -> None:
        """Default speed for drive/drive_for, e.g. (50, PERCENT).
        Starts at 50%."""
    def set_turn_velocity(self, velocity: float, units: vexEnum = ...) -> None:
        """Default speed for turns, e.g. (30, PERCENT). Starts at 50%.
        Slower turns are more accurate."""
    def set_stopping(self, mode: BrakeType.BrakeType) -> None:
        """What stop() does from now on: COAST, BRAKE, or HOLD."""
    def set_timeout(self, value: float, units: TimeUnits.TimeUnits = ...) -> None:
        """Give up on a stuck move after this long instead of pushing
        forever. SET THIS EARLY — e.g. set_timeout(5, SECONDS). Without it,
        driving into a wall blocks your program permanently (in the sim and
        on the real robot)."""
    def set_heading(self, heading: float, units: RotationUnits.RotationUnits = ...) -> None:
        """Renumber the compass: the direction the robot faces right now
        becomes this heading. No movement. Useful to make 'downfield' be 0
        wherever your run starts."""
    def set_rotation(self, rotation: float, units: RotationUnits.RotationUnits = ...) -> None:
        """Renumber the running rotation total to this value. No movement."""
    def set_turn_threshold(self, value: float) -> None:
        """How close (degrees) counts as 'done' for gyro turns. Default 1.
        Smaller = more precise but slower to settle."""
    def set_turn_constant(self, value: float) -> None:
        """Tuning knob for how aggressively gyro turns correct (default 1.0)."""
    def heading(self, units: RotationUnits.RotationUnits = ...) -> float:
        """Compass direction 0-359.9 (right turns increase it; wraps)."""
    def rotation(self, units: RotationUnits.RotationUnits = ...) -> float:
        """Running total of turning; right +, left -; never wraps."""
    def velocity(self, units: vexEnum = ...) -> float:
        """Current drive speed (average of the two sides)."""
    def current(self, units: CurrentUnits.CurrentUnits = ...) -> float: ...
    def power(self) -> float: ...
    def torque(self, units: TorqueUnits.TorqueUnits = ...) -> float: ...
    def efficiency(self) -> float: ...
    def temperature(self, units: TemperatureUnits.TemperatureUnits = ...) -> float: ...
    def is_moving(self) -> bool:
        """True while a drive_for/turn_for/turn_to move is still running.
        Use after wait=False: while drivetrain.is_moving(): wait(20, MSEC)"""
    def is_done(self) -> bool:
        """Opposite of is_moving()."""
    def is_turning(self) -> bool:
        """True while a turn command is still running."""

class SmartDrive(DriveTrain):
    """A DriveTrain plus a gyro (usually the Brain's built-in Inertial), so
    turns use the real measured heading instead of guessing from wheel
    turns. This is what VEXcode generates:
        drivetrain = SmartDrive(left_motor, right_motor, brain_inertial, 200)
    """
    def __init__(self, lm: Motor | MotorGroup, rm: Motor | MotorGroup,
                 g: Inertial | Gyro, wheelTravel: float = ...,
                 trackWidth: float = ..., wheelBase: float = ...,
                 units: DistanceUnits.DistanceUnits = ...,
                 externalGearRatio: float = ...) -> None: ...

# ============================================================
# Brain
# ============================================================

class _BrainButton:
    """One of the three buttons on the Brain's face.
    In the simulator: , = Left   . = Check   / = Right."""
    def pressing(self) -> bool:
        """True while the button is held down."""
    def pressed(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` each time the button is pressed."""
    def released(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` each time the button is let go."""

class _Battery:
    """The Brain's battery (always full in the simulator)."""
    def capacity(self) -> int:
        """Charge percent, 0-100."""
    def voltage(self, units: VoltageUnits.VoltageUnits = ...) -> float:
        """Battery voltage. Default units MV (millivolts!) — use
        voltage(VOLT) for volts."""
    def current(self) -> float:
        """Battery current in amps."""

class _Screen:
    """The Brain's little screen (160x108). In the simulator it appears in
    the panel on the right, and everything you print also shows in the
    terminal."""
    def print(self, *args: Any, precision: int = ..., opaque: bool = ..., sep: str = ...) -> None:
        """Show text at the cursor, e.g. brain.screen.print("x =", x).
        Stays on the same row — call next_row() to move down. Decimals
        round to 2 places unless you pass precision=."""
    def set_cursor(self, row: int, column: int) -> None:
        """Move the text cursor. Rows and columns start at 1."""
    def next_row(self) -> None:
        """Move the cursor to the start of the next row."""
    def new_line(self) -> None:
        """Same as next_row()."""
    def clear_row(self, row: int | None = ..., color: _AnyColor | None = ...) -> None:
        """Erase one row of text (the cursor's row if none given)."""
    def clear_screen(self, color: _AnyColor | None = ...) -> None:
        """Erase everything and put the cursor back at row 1, column 1."""
    def row(self) -> int:
        """The cursor's current row."""
    def column(self) -> int:
        """The cursor's current column."""
    def print_at(self, *args: Any, x: int = ..., y: int = ..., precision: int = ...,
                 opaque: bool = ...) -> None:
        """Show text at an exact pixel position instead of the cursor."""
    def get_string_width(self, string: str) -> int:
        """Width of a string in pixels, for lining things up."""
    def get_string_height(self, string: str) -> int:
        """Height of a string in pixels."""
    def set_font(self, fontname: FontType.FontType) -> None:
        """Change the text size, e.g. set_font(FontType.MONO20).
        (The sim panel draws all fonts at one size.)"""
    def set_pen_width(self, width: int) -> None:
        """Line thickness for drawing (sim panel draws 1px lines)."""
    def set_pen_color(self, color: _AnyColor | None = ...) -> None:
        """Color for text and drawn lines/outlines."""
    def set_fill_color(self, color: _AnyColor | None = ...) -> None:
        """Color for the inside of drawn shapes."""
    def set_origin(self, x: int, y: int) -> None:
        """Not supported in the simulator (raises an error)."""
    def set_clip_region(self, x: int, y: int, width: int, height: int) -> None:
        """Not supported in the simulator (raises an error)."""
    def draw_pixel(self, x: int, y: int) -> None:
        """Color one pixel. Screen is 160 wide, 108 tall, (0,0) top-left."""
    def draw_line(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draw a line between two points."""
    def draw_rectangle(self, x: int, y: int, width: int, height: int,
                       color: _AnyColor | None = ...) -> None:
        """Draw a rectangle; (x, y) is the top-left corner."""
    def draw_circle(self, x: int, y: int, radius: int, color: _AnyColor | None = ...) -> None:
        """Draw a circle centered on (x, y)."""
    def render(self) -> None:
        """On the real Brain this flips the drawing buffer; the sim panel
        always renders live, so this does nothing."""

class Brain:
    """The robot's Brain: screen, timer, battery, and three face buttons.
    Every program makes one: brain = Brain()."""
    screen: _Screen
    timer: Timer
    battery: _Battery
    buttonLeft: _BrainButton
    buttonCheck: _BrainButton
    buttonRight: _BrainButton
    def __init__(self) -> None: ...
    def play_sound(self, sound: SoundType.SoundType) -> None:
        """Play a built-in sound, e.g. play_sound(SoundType.TADA).
        The simulator prints it to the terminal instead of playing audio."""
    def play_note(self, octave: int, note: int, duration: int = ...) -> None:
        """Play one note (octave 3-4, note 0-6 = C D E F G A B, duration in
        ms). The simulator prints it and waits out the duration."""
    def sound_off(self) -> None:
        """Stop the current sound."""
    def program_stop(self) -> None:
        """End your program right now (the sim window stays open)."""

# ============================================================
# Sensors
# ============================================================

class Distance:
    """The laser distance sensor. In the simulator it fires a ray from the
    front of the robot (mount position set in simconfig.toml) and reports
    the first thing it hits: field perimeter, pyramids, or the goal poles.
    Bean bags and the low floor strips are too low to see — and the raised
    beams are above it unless you mount it at ~6 inches. Press `d` in the
    sim window to see the ray."""

    port: int
    def __init__(self, port: int) -> None: ...
    def is_object_detected(self) -> bool:
        """True if something is within range (20mm to 2000mm)."""
    def object_distance(self, units: DistanceUnits.DistanceUnits = ...) -> float:
        """Distance to the nearest object, in MM by default. Range is
        20-2000mm; with nothing in range it returns the maximum (2000mm),
        so `while object_distance(MM) > 300:` loops work."""
    def object_velocity(self) -> float:
        """How fast the object ahead is approaching, in meters/second
        (positive = getting closer)."""
    def object_size(self) -> ObjectSizeType.ObjectSizeType:
        """Rough size of the detected object (NONE if nothing in range)."""
    def installed(self) -> bool: ...
    def changed(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` when the measured distance changes."""

class Bumper:
    """The bumper switch. In the simulator it presses when the robot is
    pushing against something solid in front of it."""
    port: int
    def __init__(self, port: int) -> None: ...
    def pressing(self) -> int:
        """1 while pressed, 0 while not. Works in an if:
        `if bumper.pressing():`"""
    def pressed(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` each time the bumper gets pressed."""
    def released(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` each time the bumper is released."""

class Touchled:
    """A touch-sensitive LED button. In the simulator its color shows as a
    dot in the side panel, and keyboard keys 1-4 press the first four
    Touchleds you created."""
    port: int
    def __init__(self, port: int) -> None: ...
    def on(self, value: _AnyColor = ...) -> None:
        """Light up (optionally with a color) at full brightness."""
    def off(self) -> None:
        """Turn the light off."""
    def toggle(self) -> None:
        """Flip between on and off."""
    def set_color(self, color: _AnyColor = ...) -> None:
        """Change the light's color, e.g. set_color(Color.RED)."""
    def set_brightness(self, brightness: int) -> None:
        """Brightness 0-100."""
    def set_fade(self, type: FadeType.FadeType) -> None:
        """How color changes blend (cosmetic; no effect in the sim)."""
    def set_blink(self, color: _AnyColor, ontime: float = ..., offtime: float = ...) -> None:
        """Blink a color (the sim panel shows it steady)."""
    def pressing(self) -> int:
        """1 while touched, 0 while not (keys 1-4 in the sim window)."""
    def pressed(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` each time it's touched."""
    def released(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` each time the touch ends."""
    def installed(self) -> bool: ...

class Optical:
    """The color/light sensor. In the simulator it looks at whatever bean
    bag sits right in front of the robot and reports its color — useful to
    check what your intake is about to grab."""
    port: int
    def __init__(self, port: int) -> None: ...
    def set_light(self, state: Any) -> None:
        """Turn the sensor's little lamp on/off (no effect in the sim)."""
    def set_light_power(self, value: int) -> None:
        """Lamp brightness 0-100 (no effect in the sim)."""
    def object_detect_threshold(self, value: int) -> int:
        """Tune how close something must be to count as 'near'."""
    def is_near_object(self) -> bool:
        """True when a bean bag is right in front of the robot."""
    def color(self) -> Color.DefinedColor:
        """The color it sees: Color.RED, Color.BLUE or Color.YELLOW for a
        bag in front; Color.BLACK when there's nothing."""
    def brightness(self, readraw: bool = ...) -> float:
        """How bright the view is, as a percent."""
    def hue(self) -> float:
        """The color as a hue angle 0-359 (red~0, yellow~60, blue~220)."""
    def rgb(self, raw: bool = ...) -> tuple[int, int, int, int]:
        """The color as (red, green, blue, brightness)."""
    def installed(self) -> bool: ...
    def object_detected(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` when something appears in front."""
    def object_lost(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` when it goes away."""

class ColorSensor:
    def __init__(self, port: int) -> None:
        """Not simulated — use Optical(port) instead (the 2nd-gen sensor)."""

class Pneumatic:
    def __init__(self, port: int) -> None:
        """Not simulated (v1) — creating one raises an error."""

class Vision:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Not simulated — creating one raises an error."""

class AiVision:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Not simulated — use Distance or Optical in the sim instead."""

class Sonar:
    def __init__(self, port: int) -> None:
        """1st-gen sensor, not simulated — use Distance(port)."""

# ============================================================
# Controller (keyboard-driven in the sim)
# ============================================================

class _ControllerAxis:
    """One joystick direction. position() is -100..100.
    Sim keyboard: WASD = left stick (A vertical, B horizontal),
    arrow keys = right stick (D vertical, C horizontal)."""
    def position(self) -> int:
        """Where the stick is, -100 (full one way) to 100 (full the other),
        0 = centered."""
    def changed(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` when the stick moves."""

class _ControllerButton:
    """One controller button. Sim keyboard: z/x = L up/down, n/m = R
    up/down, r/f = E up/down, t/g = F up/down."""
    def pressing(self) -> bool:
        """True while held down."""
    def pressed(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` each time it's pressed."""
    def released(self, callback: Callable[..., Any], arg: tuple[Any, ...] = ...) -> None:
        """Run `callback` each time it's released."""

class Controller:
    """The handheld controller. In the simulator you drive it with the
    keyboard while the sim window is focused: WASD = left stick, arrows =
    right stick, z/x n/m r/f t/g = the button pairs."""
    axisA: _ControllerAxis
    axisB: _ControllerAxis
    axisC: _ControllerAxis
    axisD: _ControllerAxis
    buttonEUp: _ControllerButton
    buttonEDown: _ControllerButton
    buttonFUp: _ControllerButton
    buttonFDown: _ControllerButton
    buttonLUp: _ControllerButton
    buttonLDown: _ControllerButton
    buttonRUp: _ControllerButton
    buttonRDown: _ControllerButton
    buttonL3: _ControllerButton
    buttonR3: _ControllerButton
    remote_control_code_enabled: bool
    def __init__(self) -> None: ...
    def rumble(self, *args: Any, **kwargs: Any) -> None:
        """Not simulated — raises an error."""

# ============================================================
# Console helpers and errors
# ============================================================

def clear_console() -> None:
    """Print a separator in the terminal (clears the console on a real
    Brain's connected computer)."""

def set_console_text_color(color: _AnyColor) -> None:
    """Change terminal text color (no effect in the simulator)."""

class VexSimError(Exception):
    """Something went wrong inside the simulator itself."""

class VexSimNotImplemented(VexSimError):
    """You used a VEX feature the simulator doesn't model (on purpose —
    it raises instead of silently doing nothing)."""
