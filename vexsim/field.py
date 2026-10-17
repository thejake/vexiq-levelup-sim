"""VEX IQ 2026-27 "Level Up" field — Skills layout.

Frame: landscape, inches, origin bottom-left. X runs along the long side
(0-97), Y along the short side (0-73), matching the VEXcode VR field image.
Geometry transcribed from the game manual Appendix A drawing (see
reference/ and HANDOFF.md for provenance and open questions).
"""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import AABB, Circle

FIELD_W = 97.0
FIELD_H = 73.0

# Black tape grid lines at 6.5 + 12k on both axes.
TAPE_XS = [6.5 + 12 * k for k in range(8) if 6.5 + 12 * k < FIELD_W]
TAPE_YS = [6.5 + 12 * k for k in range(6) if 6.5 + 12 * k < FIELD_H]

BAG_W = 4.0  # along X as placed at setup
BAG_H = 3.0

# ---- Wall structures and floor barriers (manual Appendix A, page A4) ----
# The "wall structures" are NOT walls: each is a 0.84"-diameter yellow rod
# elevated at 6.25" (center height), running from the field perimeter to a
# support bracket. Beneath and beyond it runs a 0.75"-tall, 1"-wide floor
# strip with 16.5-degree ramped edges (drive-over-able).

BEAM_DIAMETER = 0.84
BEAM_CENTER_HEIGHT = 6.25
BEAM_CLEARANCE = BEAM_CENTER_HEIGHT - BEAM_DIAMETER / 2   # ~5.8": fit under this
STRIP_W = 1.0
STRIP_H = 0.75

# Elevated rods (plan footprint).
BEAMS = [
    AABB(60.5 - BEAM_DIAMETER / 2, 0.5, 60.5 + BEAM_DIAMETER / 2, 26.5),
    AABB(36.5 - BEAM_DIAMETER / 2, 46.5, 36.5 + BEAM_DIAMETER / 2, 72.5),
]

# Triangular support brackets at the beams' inner ends (6.25" tall — solid).
BEAM_BRACKETS = [
    AABB(60.0, 26.5, 61.0, 27.6),
    AABB(36.0, 45.4, 37.0, 46.5),
]

# Ramped floor strips: under each beam, continuing past the bracket toward
# the support post ("floor barrier").
STRIPS = [
    AABB(60.5 - STRIP_W / 2, 0.5, 60.5 + STRIP_W / 2, 39.0),
    AABB(36.5 - STRIP_W / 2, 34.0, 36.5 + STRIP_W / 2, 72.5),
]

# Pyramid corner goals (19.25" on-field footprint per Appendix A page A7;
# steps 2.5/5/8/10" tall — solid to the robot). Bottom-right red is
# inferred from the Skills start position; verify in VEX VR.
PYRAMIDS = {
    "blue": AABB(0.0, FIELD_H - 19.25, 19.25, FIELD_H),
    "red": AABB(FIELD_W - 19.25, 0.0, FIELD_W, 19.25),
}

# L4 goals: inverted cones (7" octagon top) on 24"-tall poles. The robot
# only collides with the pole; the cone top is at 24".
L4_TOPS = [Circle(60.5, 42.5, 3.5), Circle(36.5, 30.5, 3.5)]
L4_POLES = [Circle(60.5, 42.5, 0.9), Circle(36.5, 30.5, 0.9)]

# Beam-line support posts: a pole on a low base disc. The base makes the
# effective collision radius bigger than the pole the distance sensor sees.
SUPPORT_POSTS = [Circle(60.5, 30.5, 2.0), Circle(36.5, 42.5, 2.0)]
SUPPORT_POLES = [Circle(60.5, 30.5, 0.9), Circle(36.5, 42.5, 0.9)]

# Floor goals on the short ends (score zone; not solid). Boundary tape at
# 7.00 / 90.00 per Appendix A page A7.
FLOOR_GOALS = {
    "red": AABB(90.0, 18.5, FIELD_W, 54.5),
    "blue": AABB(0.0, 18.5, 7.0, 54.5),
}

# Load zones (not solid).
LOAD_ZONES = {
    "red": AABB(0.0, 0.0, 7.0, 18.5),
    "blue": AABB(90.0, 54.5, FIELD_W, FIELD_H),
}

# Skills start zone (approximate), bottom edge.
START_ZONE = AABB(42.5, 0.0, 54.5, 20.0)

# Bean bag starting positions (centers).
BAG_STARTS = {
    "blue": [(84.5, 48.5), (84.5, 36.5), (84.5, 24.5), (78.5, 66.5),
             (66.5, 66.5), (66.5, 36.5), (66.5, 6.5), (48.5, 30.5)],
    "red": [(48.5, 42.5), (30.5, 66.5), (30.5, 36.5), (30.5, 6.5),
            (18.5, 6.5), (12.5, 48.5), (12.5, 36.5), (12.5, 24.5)],
    "yellow": [(42.5, 30.5), (42.5, 42.5), (54.5, 30.5), (54.5, 42.5)],
}


@dataclass
class Bag:
    color: str           # "red" | "blue" | "yellow"
    x: float             # center
    y: float
    carried: bool = False

    def aabb(self) -> AABB:
        return AABB(self.x - BAG_W / 2, self.y - BAG_H / 2,
                    self.x + BAG_W / 2, self.y + BAG_H / 2)


def make_bags() -> list[Bag]:
    bags = []
    for color, positions in BAG_STARTS.items():
        for x, y in positions:
            bags.append(Bag(color, x, y))
    return bags


# ---- obstacle sets (parameterized by robot/sensor geometry) ----

def perimeter_segments():
    return [
        ((0.0, 0.0), (FIELD_W, 0.0)),
        ((FIELD_W, 0.0), (FIELD_W, FIELD_H)),
        ((FIELD_W, FIELD_H), (0.0, FIELD_H)),
        ((0.0, FIELD_H), (0.0, 0.0)),
    ]


def solid_rects(robot_height_in: float, strips_block: bool) -> list[AABB]:
    """Rectangular obstacles the ROBOT cannot drive through. The elevated
    beams only block robots too tall to fit under them; the ramped floor
    strips only block if configured to."""
    rects = list(PYRAMIDS.values()) + list(BEAM_BRACKETS)
    if robot_height_in >= BEAM_CLEARANCE:
        rects += list(BEAMS)
    if strips_block:
        rects += list(STRIPS)
    return rects


def solid_circles() -> list[Circle]:
    """The L4 goal poles and the beam support posts (pole + base disc)."""
    return list(L4_POLES) + list(SUPPORT_POSTS)


def bag_blocking_rects() -> list[AABB]:
    """What a pushed bean bag can't slide through (it slides over strips)."""
    return list(PYRAMIDS.values()) + list(BEAM_BRACKETS)


def distance_visible_segments(sensor_height_in: float):
    """Segments the DISTANCE SENSOR can see at its mount height: perimeter,
    pyramids (up to 10" tall), and the beams only if the sensor happens to
    be at beam height. Floor strips and bean bags are too low."""
    segs = list(perimeter_segments())
    for rect in PYRAMIDS.values():
        segs.extend(rect.segments())
    if abs(sensor_height_in - BEAM_CENTER_HEIGHT) <= 1.0:
        for rect in BEAMS:
            segs.extend(rect.segments())
    return segs


def distance_visible_circles() -> list[Circle]:
    """The sensor sees the thin poles (24" tall), not base discs/cone tops."""
    return list(L4_POLES) + list(SUPPORT_POLES)
