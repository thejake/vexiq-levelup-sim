"""Simulator configuration: robot geometry, device mounting, realism knobs.

Defaults match a Flop-like hero bot in the Skills start position. Everything
can be overridden in `simconfig.toml` at the repo root (or next to the user's
program) — see README for the format.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field


@dataclass
class RobotConfig:
    # Footprint (inches). Starting size limit is 11 x 20 x 15 tall; a
    # Flop-ish bot is smaller than the limit.
    length_in: float = 11.0
    width_in: float = 9.0
    # Height decides whether the robot fits under the elevated beams
    # (~5.8" clearance). Default: too tall.
    height_in: float = 11.0

    # The 0.75"-tall ramped floor strips: real robots can usually drive
    # over them (16.5-degree ramps). False = crossable at reduced speed;
    # true = treat as solid (conservative).
    strips_block: bool = False
    strip_slow_factor: float = 0.6  # speed multiplier while crossing a strip

    # Start pose: Skills start zone, facing +Y (per the skills layout).
    start_x: float = 48.5
    start_y: float = 9.0
    start_theta_deg: float = 90.0  # math convention: 90 = facing +Y

    # Motor model
    motor_max_rpm: float = 120.0       # IQ smart motor free speed at 100%
    motor_accel_dps2: float = 2000.0   # deg/s^2 toward target speed

    # Fallback drivetrain geometry when user code drives raw motors
    # (no DriveTrain/SmartDrive constructed) and drive ports are configured.
    left_drive_ports: list[int] = field(default_factory=list)
    right_drive_ports: list[int] = field(default_factory=list)
    fallback_wheel_travel_mm: float = 200.0
    fallback_track_width_mm: float = 173.0

    # Intake: motors on these ports grab/eject bean bags.
    intake_ports: list[int] = field(default_factory=lambda: [6])

    # Arm: motors on these ports raise the intake for pyramid placement.
    # Arm height = motor position (deg) * arm_in_per_deg; the drop point
    # also reaches forward as the arm rises (four-bar-like: ~0.9" out per
    # 1" up). Default: 400 deg -> 10" high, dropping ~11.5" past the front,
    # which lands on L3 when parked against the pyramid.
    arm_ports: list[int] = field(default_factory=lambda: [10])
    arm_in_per_deg: float = 0.025
    # A bag can be picked up when its center is within this zone in front
    # of the robot (inches).
    pickup_reach_in: float = 3.0
    pickup_halfwidth_in: float = 3.5

    # Distance sensor mount: offset from robot center (inches, robot frame:
    # +x forward, +y left), facing relative to robot heading (deg), and
    # height off the floor (decides whether it can see the 6.25" beams).
    dist_forward_in: float = 5.5
    dist_lateral_in: float = 0.0
    dist_facing_deg: float = 0.0
    dist_height_in: float = 3.0
    dist_max_range_mm: float = 2000.0  # official range 20-2000 mm

    # Start carrying the Skills yellow preload?
    preload_yellow: bool = True


@dataclass
class Realism:
    # 0.0 = off. wheel_slip scales down actual travel by up to this fraction.
    wheel_slip: float = 0.0
    # Gaussian noise sigma added to sensor reads.
    heading_noise_deg: float = 0.0
    distance_noise_mm: float = 0.0
    # After a turn completes, overshoot by ~N(overshoot_deg, overshoot_deg/2).
    turn_overshoot_deg: float = 0.0
    # Chance (0..1) that a pyramid placement slips one level down
    # (L3 -> L2, L1 -> floor). Bean bags are floppy; placements miss.
    place_slip_prob: float = 0.0


@dataclass
class SimConfig:
    robot: RobotConfig = field(default_factory=RobotConfig)
    realism: Realism = field(default_factory=Realism)
    speed: float = 1.0           # sim speed multiplier
    pixels_per_inch: int = 9
    skills_loads: int = 8        # extra bags available via the load zone


def _apply(obj, data: dict, label: str) -> None:
    for key, value in data.items():
        if not hasattr(obj, key):
            raise SystemExit(f"[vexsim] unknown setting '{key}' in [{label}] of simconfig.toml")
        setattr(obj, key, value)


def load_config(script_path: str | None = None) -> SimConfig:
    """Load simconfig.toml from next to the user script, the CWD, or the
    repo root (first found wins)."""
    cfg = SimConfig()
    candidates = []
    if script_path:
        candidates.append(os.path.join(os.path.dirname(os.path.abspath(script_path)), "simconfig.toml"))
    candidates.append(os.path.join(os.getcwd(), "simconfig.toml"))
    candidates.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "simconfig.toml"))
    for path in candidates:
        if os.path.isfile(path):
            with open(path, "rb") as f:
                data = tomllib.load(f)
            _apply(cfg.robot, data.get("robot", {}), "robot")
            _apply(cfg.realism, data.get("realism", {}), "realism")
            for key in ("speed", "pixels_per_inch", "skills_loads"):
                if key in data:
                    setattr(cfg, key, data[key])
            print(f"[vexsim] loaded config from {path}")
            break
    return cfg
