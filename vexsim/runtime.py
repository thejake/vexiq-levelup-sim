"""Shared runtime state between the `vex` API module and the simulator engine.

The `vex` module imports this (and nothing else from vexsim) so there are no
circular imports. The runner populates `clock`, `world`, and `config` before
user code executes.
"""

from __future__ import annotations


class VexSimError(Exception):
    """Base class for simulator errors."""


class VexSimNotImplemented(VexSimError):
    """Raised when user code touches a VEX API feature the simulator
    does not model. Never silently no-op."""

    def __init__(self, feature: str, hint: str = ""):
        msg = f"[vexsim] '{feature}' is not implemented in the simulator."
        if hint:
            msg += " " + hint
        super().__init__(msg)


# Populated by vexsim.__main__ before user code runs.
clock = None   # vexsim.clock.SimClock
world = None   # vexsim.world.World
config = None  # vexsim.config.SimConfig

# Every vex device object registers itself here at construction.
devices: list = []

# One-time console notes (so partially-modeled features are visible, not silent)
_noted: set = set()


def note_once(key: str, message: str) -> None:
    if key not in _noted:
        _noted.add(key)
        print(f"[vexsim] {message}")


def require_sim(what: str = "the vex API"):
    if clock is None or world is None:
        raise VexSimError(
            f"{what} was used but the simulator is not running. "
            "Run your program with: python -m vexsim yourfile.py"
        )
    return world


def register(device) -> None:
    devices.append(device)
