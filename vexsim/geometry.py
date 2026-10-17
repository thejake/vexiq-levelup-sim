"""2D geometry helpers: oriented rectangles, collision tests, raycasts.

All field math is in inches; angles in degrees, CCW-positive, 0 = +X
(standard math convention). The VEX clockwise heading is derived in the
vex API layer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class AABB:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2

    def contains_aabb(self, other: "AABB") -> bool:
        return (other.x0 >= self.x0 and other.x1 <= self.x1
                and other.y0 >= self.y0 and other.y1 <= self.y1)

    def overlaps(self, other: "AABB") -> bool:
        return not (other.x0 >= self.x1 or other.x1 <= self.x0
                    or other.y0 >= self.y1 or other.y1 <= self.y0)

    def contains_point(self, x: float, y: float) -> bool:
        return self.x0 <= x <= self.x1 and self.y0 <= y <= self.y1

    def corners(self) -> list[tuple[float, float]]:
        return [(self.x0, self.y0), (self.x1, self.y0),
                (self.x1, self.y1), (self.x0, self.y1)]

    def segments(self) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        c = self.corners()
        return [(c[i], c[(i + 1) % 4]) for i in range(4)]


@dataclass(frozen=True)
class Circle:
    cx: float
    cy: float
    r: float


def oriented_rect_corners(cx: float, cy: float, length: float, width: float,
                          theta_deg: float) -> list[tuple[float, float]]:
    """Corners of a rectangle centered at (cx, cy), `length` along the
    heading direction, `width` across it."""
    t = math.radians(theta_deg)
    ux, uy = math.cos(t), math.sin(t)      # forward
    vx, vy = -math.sin(t), math.cos(t)     # left
    hl, hw = length / 2, width / 2
    return [
        (cx + ux * hl + vx * hw, cy + uy * hl + vy * hw),
        (cx + ux * hl - vx * hw, cy + uy * hl - vy * hw),
        (cx - ux * hl - vx * hw, cy - uy * hl - vy * hw),
        (cx - ux * hl + vx * hw, cy - uy * hl + vy * hw),
    ]


def _project(poly: list[tuple[float, float]], ax: float, ay: float) -> tuple[float, float]:
    dots = [px * ax + py * ay for px, py in poly]
    return min(dots), max(dots)


def polys_collide(a: list[tuple[float, float]], b: list[tuple[float, float]]) -> bool:
    """Separating-axis test for two convex polygons."""
    for poly in (a, b):
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            # axis = edge normal
            ax, ay = y2 - y1, x1 - x2
            amin, amax = _project(a, ax, ay)
            bmin, bmax = _project(b, ax, ay)
            if amax < bmin or bmax < amin:
                return False
    return True


def poly_circle_collide(poly: list[tuple[float, float]], c: Circle) -> bool:
    # Inside test via SAT on polygon axes plus axis to closest vertex.
    n = len(poly)
    axes = []
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        axes.append((y2 - y1, x1 - x2))
    # axis from circle center to closest polygon vertex
    best = min(poly, key=lambda p: (p[0] - c.cx) ** 2 + (p[1] - c.cy) ** 2)
    axes.append((best[0] - c.cx, best[1] - c.cy))
    for ax, ay in axes:
        norm = math.hypot(ax, ay)
        if norm == 0:
            continue
        ax, ay = ax / norm, ay / norm
        pmin, pmax = _project(poly, ax, ay)
        cproj = c.cx * ax + c.cy * ay
        if pmax < cproj - c.r or cproj + c.r < pmin:
            return False
    return True


def poly_aabb(poly: list[tuple[float, float]]) -> AABB:
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return AABB(min(xs), min(ys), max(xs), max(ys))


# ---- raycasting ----

def ray_segment(ox: float, oy: float, dx: float, dy: float,
                p1: tuple[float, float], p2: tuple[float, float]) -> float | None:
    """Distance along ray (ox,oy)+(dx,dy)*t to segment p1-p2, or None."""
    x1, y1 = p1
    x2, y2 = p2
    ex, ey = x2 - x1, y2 - y1
    denom = dx * ey - dy * ex
    if abs(denom) < 1e-12:
        return None
    t = ((x1 - ox) * ey - (y1 - oy) * ex) / denom
    if t < 0:
        return None
    if abs(ex) > abs(ey):
        s = (ox + t * dx - x1) / ex
    else:
        s = (oy + t * dy - y1) / ey
    if 0.0 <= s <= 1.0:
        return t
    return None


def ray_circle(ox: float, oy: float, dx: float, dy: float, c: Circle) -> float | None:
    """Distance along unit-ish ray to circle, or None."""
    fx, fy = ox - c.cx, oy - c.cy
    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    cc = fx * fx + fy * fy - c.r * c.r
    disc = b * b - 4 * a * cc
    if disc < 0:
        return None
    sq = math.sqrt(disc)
    t1 = (-b - sq) / (2 * a)
    t2 = (-b + sq) / (2 * a)
    if t1 >= 0:
        return t1
    if t2 >= 0:
        return t2
    return None


def normalize_deg(a: float) -> float:
    """Normalize to [0, 360)."""
    return a % 360.0


def signed_err_deg(target: float, current: float) -> float:
    """Shortest signed angular difference target-current in (-180, 180]."""
    d = (target - current) % 360.0
    if d > 180.0:
        d -= 360.0
    return d
