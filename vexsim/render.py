"""pygame renderer: field, robot, bean bags, HUD with brain screen.

Coordinate transform: field inches -> screen pixels, Y flipped (field origin
is bottom-left; screen origin is top-left).
"""

from __future__ import annotations

import math

import pygame

from . import field
from .geometry import oriented_rect_corners

# colors
BG = (24, 26, 28)
FIELD_GRAY = (72, 74, 76)
TILE_LINE = (64, 66, 68)
TAPE = (30, 30, 30)
PERIMETER = (150, 150, 155)
YELLOW = (235, 200, 40)
YELLOW_DIM = (160, 140, 50)
RED = (205, 60, 60)
BLUE = (70, 110, 220)
BAG_COLORS = {"red": (210, 70, 70), "blue": (80, 120, 230), "yellow": (240, 210, 60)}
ROBOT = (230, 230, 235)
ROBOT_FILL = (45, 90, 60)
HUD_BG = (18, 19, 20)
HUD_TEXT = (210, 212, 215)
HUD_DIM = (130, 132, 135)
SCREEN_BG = (10, 30, 10)
SCREEN_TEXT = (120, 230, 120)

PANEL_W = 300
MARGIN = 14


class Renderer:
    def __init__(self, world, scale: int):
        self.world = world
        self.scale = scale
        self.show_ray = True
        w = int(field.FIELD_W * scale) + 2 * MARGIN + PANEL_W
        h = int(field.FIELD_H * scale) + 2 * MARGIN
        self.surface = pygame.display.set_mode((w, h))
        pygame.display.set_caption("vexsim — VEX IQ Level Up")
        self.font = pygame.font.SysFont("Menlo", 13)
        self.font_small = pygame.font.SysFont("Menlo", 11)
        self.font_screen = pygame.font.SysFont("Menlo", 12)

    # field inches -> screen px
    def sx(self, x: float) -> int:
        return MARGIN + int(x * self.scale)

    def sy(self, y: float) -> int:
        return MARGIN + int((field.FIELD_H - y) * self.scale)

    def rect_px(self, r) -> pygame.Rect:
        return pygame.Rect(self.sx(r.x0), self.sy(r.y1),
                           int((r.x1 - r.x0) * self.scale),
                           int((r.y1 - r.y0) * self.scale))

    def draw(self, sim_time: float, speed: float, paused: bool) -> None:
        s = self.surface
        w = self.world
        s.fill(BG)

        # field surface
        pygame.draw.rect(s, FIELD_GRAY, self.rect_px(
            field.AABB(0, 0, field.FIELD_W, field.FIELD_H)))

        # tile seams every 12 in from the 6.5 tape offset, light
        for x in range(0, int(field.FIELD_W) + 1, 12):
            pygame.draw.line(s, TILE_LINE, (self.sx(x), self.sy(0)), (self.sx(x), self.sy(field.FIELD_H)))
        for y in range(0, int(field.FIELD_H) + 1, 12):
            pygame.draw.line(s, TILE_LINE, (self.sx(0), self.sy(y)), (self.sx(field.FIELD_W), self.sy(y)))

        # black tape lines
        for x in field.TAPE_XS:
            pygame.draw.line(s, TAPE, (self.sx(x), self.sy(0)), (self.sx(x), self.sy(field.FIELD_H)), 2)
        for y in field.TAPE_YS:
            pygame.draw.line(s, TAPE, (self.sx(0), self.sy(y)), (self.sx(field.FIELD_W), self.sy(y)), 2)

        # zones
        self._zone(field.FLOOR_GOALS["red"], RED, 70, "RED GOAL")
        self._zone(field.FLOOR_GOALS["blue"], BLUE, 70, "BLUE GOAL")
        self._zone(field.LOAD_ZONES["red"], RED, 35, "LOAD")
        self._zone(field.LOAD_ZONES["blue"], BLUE, 35, "LOAD")
        self._zone(field.START_ZONE, (200, 200, 200), 25, "START")

        # pyramids: footprint plus the L2/L3 level rings, corner-anchored
        for color, rect in field.PYRAMIDS.items():
            c = RED if color == "red" else BLUE
            pygame.draw.rect(s, c, self.rect_px(rect), 3)
            cx, cy = field.PYRAMID_CORNERS[color]
            for edge, _h, _pts, name in field.PYRAMID_LEVELS[:2]:
                x0, x1 = (0.0, edge) if cx == 0 else (cx - edge, cx)
                y0, y1 = (0.0, edge) if cy == 0 else (cy - edge, cy)
                pygame.draw.rect(s, c, self.rect_px(field.AABB(x0, y0, x1, y1)), 2)
            self._label(rect.cx, rect.cy, "L1-L3", c)

        # ramped floor strips (0.75" tall, drive-over-able)
        for rect in field.STRIPS:
            r = self.rect_px(rect)
            r.width = max(r.width, 3)
            pygame.draw.rect(s, YELLOW_DIM, r)
        # elevated beams (rod at 6.25") — bright, with a dark outline to read
        # as "above the floor"
        for rect in field.BEAMS:
            r = self.rect_px(rect).inflate(4, 0)
            pygame.draw.rect(s, YELLOW, r)
            pygame.draw.rect(s, (40, 40, 40), r, 1)
        # beam support brackets (solid)
        for rect in field.BEAM_BRACKETS:
            pygame.draw.rect(s, (120, 105, 40), self.rect_px(rect))

        # beam support posts: base disc + pole
        for base, pole in zip(field.SUPPORT_POSTS, field.SUPPORT_POLES):
            pygame.draw.circle(s, (70, 70, 72), (self.sx(base.cx), self.sy(base.cy)),
                               int(base.r * self.scale))
            pygame.draw.circle(s, YELLOW, (self.sx(pole.cx), self.sy(pole.cy)),
                               int(pole.r * self.scale))

        # L4 goals: cone top (octagon, 24" up — not an obstacle) + pole
        for top, pole in zip(field.L4_TOPS, field.L4_POLES):
            pts = []
            for i in range(8):
                a = math.pi / 8 + i * math.pi / 4
                pts.append((self.sx(top.cx + top.r * math.cos(a)),
                            self.sy(top.cy + top.r * math.sin(a))))
            pygame.draw.polygon(s, YELLOW_DIM, pts, 2)
            pygame.draw.circle(s, YELLOW, (self.sx(pole.cx), self.sy(pole.cy)),
                               int(pole.r * self.scale))

        # perimeter
        pygame.draw.rect(s, PERIMETER, self.rect_px(
            field.AABB(0, 0, field.FIELD_W, field.FIELD_H)), 3)

        # bean bags
        for bag in w.bags:
            if bag.carried:
                continue
            bb = bag.aabb()
            r = self.rect_px(bb)
            pygame.draw.rect(s, BAG_COLORS[bag.color], r, border_radius=3)
            pygame.draw.rect(s, (20, 20, 20), r, 1, border_radius=3)

        # distance sensor ray
        if self.show_ray:
            self._draw_ray()

        # robot
        self._draw_robot()

        # HUD
        self._draw_hud(sim_time, speed, paused)

        pygame.display.flip()

    def _zone(self, rect, color, alpha, label) -> None:
        r = self.rect_px(rect)
        overlay = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        overlay.fill((*color, alpha))
        self.surface.blit(overlay, r.topleft)
        self._label(rect.cx, rect.cy, label, (*color,))

    def _label(self, x, y, text, color) -> None:
        img = self.font_small.render(text, True, color)
        self.surface.blit(img, (self.sx(x) - img.get_width() // 2,
                                self.sy(y) - img.get_height() // 2))

    def _draw_ray(self) -> None:
        w = self.world
        r = w.config.robot
        with w._lock:
            x, y, theta = w.x, w.y, w.theta
        t = math.radians(theta)
        fx, fy = math.cos(t), math.sin(t)
        lx, ly = -math.sin(t), math.cos(t)
        ox = x + fx * r.dist_forward_in + lx * r.dist_lateral_in
        oy = y + fy * r.dist_forward_in + ly * r.dist_lateral_in
        mm = w._last_ray_mm
        length_in = (mm / 25.4) if mm is not None else r.dist_max_range_mm / 25.4
        a = math.radians(theta + r.dist_facing_deg)
        ex = ox + math.cos(a) * length_in
        ey = oy + math.sin(a) * length_in
        color = (120, 220, 120) if mm is not None else (90, 90, 90)
        pygame.draw.line(self.surface, color, (self.sx(ox), self.sy(oy)),
                         (self.sx(ex), self.sy(ey)), 1)
        if mm is not None:
            pygame.draw.circle(self.surface, color, (self.sx(ex), self.sy(ey)), 3)

    def _draw_robot(self) -> None:
        w = self.world
        cfg = w.config.robot
        with w._lock:
            x, y, theta = w.x, w.y, w.theta
        poly = oriented_rect_corners(x, y, cfg.length_in, cfg.width_in, theta)
        pts = [(self.sx(px), self.sy(py)) for px, py in poly]
        pygame.draw.polygon(self.surface, ROBOT_FILL, pts)
        pygame.draw.polygon(self.surface, ROBOT, pts, 2)
        # heading arrow
        t = math.radians(theta)
        tip = (self.sx(x + math.cos(t) * cfg.length_in / 2),
               self.sy(y + math.sin(t) * cfg.length_in / 2))
        pygame.draw.line(self.surface, ROBOT, (self.sx(x), self.sy(y)), tip, 2)
        pygame.draw.circle(self.surface, ROBOT, tip, 3)
        # carried bag
        if w.carried is not None:
            bag = w.carried
            r = self.rect_px(bag.aabb())
            pygame.draw.rect(self.surface, BAG_COLORS[bag.color], r, border_radius=3)
            pygame.draw.rect(self.surface, (255, 255, 255), r, 2, border_radius=3)

    # ---- HUD ----

    def _draw_hud(self, sim_time, speed, paused) -> None:
        w = self.world
        panel_x = self.surface.get_width() - PANEL_W
        pygame.draw.rect(self.surface, HUD_BG,
                         pygame.Rect(panel_x, 0, PANEL_W, self.surface.get_height()))
        x = panel_x + 14
        y = 12

        def line(text, color=HUD_TEXT, font=None, dy=18):
            nonlocal y
            img = (font or self.font).render(text, True, color)
            self.surface.blit(img, (x, y))
            y += dy

        status = "PAUSED" if paused else f"{speed:g}x"
        line(f"t = {sim_time:7.2f} s   [{status}]")
        line(f"program: {w.program_status}",
             HUD_DIM if w.program_status == "running" else (240, 180, 90))
        y += 4
        line(f"score   red {w.score['red']} pts   blue {w.score['blue']} pts", (240, 220, 140))
        carried = w.carried.color if w.carried else "-"
        arm = w._arm_height_in()
        line(f"carrying: {carried}   arm: {arm:4.1f} in   loads: {w.loads_remaining}")
        y += 6

        # pose and sensors
        with w._lock:
            px, py, ptheta = w.x, w.y, w.theta
        heading = (w._theta0 - ptheta) % 360
        line(f"pose  x {px:5.1f}  y {py:5.1f} in", HUD_DIM)
        line(f"      x {px * 25.4:5.0f}  y {py * 25.4:5.0f} mm", HUD_DIM)
        line(f"heading {heading:6.1f}°  (cw, 0 = start)", HUD_DIM)
        mm = w._last_ray_mm
        line(f"distance: {mm:5.0f} mm" if mm is not None else "distance: ---", HUD_DIM)
        line(f"bumper: {'PRESSED' if w.bumper_pressing() else '-'}", HUD_DIM)
        y += 6

        # motors
        import vex
        from . import runtime
        shown = 0
        for dev in runtime.devices:
            if hasattr(dev, "_actual_dps") and shown < 8:
                rpm = dev._actual_dps / 6.0 / max(dev.gear_ratio, 1e-6)
                line(f"M{dev.port:<2} {rpm:7.1f} rpm  pos {dev._pos:8.1f}°",
                     HUD_DIM, self.font_small, 15)
                shown += 1
        y += 6

        # touchleds
        tx = x
        for dev in runtime.devices:
            if isinstance(dev, vex.Touchled):
                rgb = dev.color_rgb or (60, 60, 60)
                pygame.draw.circle(self.surface, rgb, (tx + 8, y + 8), 8)
                img = self.font_small.render(f"{dev.index + 1}", True, HUD_DIM)
                self.surface.blit(img, (tx + 4, y + 18))
                tx += 28
        if tx != x:
            y += 36

        # brain screen
        if w.brain is not None:
            line("brain screen", HUD_DIM, self.font_small, 16)
            sw, sh = PANEL_W - 28, 130
            screen_rect = pygame.Rect(x, y, sw, sh)
            pygame.draw.rect(self.surface, SCREEN_BG, screen_rect)
            pygame.draw.rect(self.surface, (60, 90, 60), screen_rect, 1)
            rows, draws = w.brain.screen.snapshot()
            for i, row in enumerate(rows):
                if row:
                    img = self.font_screen.render(row[:36], True, SCREEN_TEXT)
                    self.surface.blit(img, (x + 6, y + 4 + i * 14))
            # pixel draws, scaled 160x108 -> panel
            kx, ky = sw / 160.0, sh / 108.0
            for kind, dx_, dy_, extra, color in draws:
                rgb = getattr(color, "_rgb", (255, 255, 255))
                if kind == "pixel":
                    self.surface.set_at((x + int(dx_ * kx), y + int(dy_ * ky)), rgb)
                elif kind == "line":
                    x2, y2 = extra
                    pygame.draw.line(self.surface, rgb,
                                     (x + dx_ * kx, y + dy_ * ky),
                                     (x + x2 * kx, y + y2 * ky))
                elif kind == "rect":
                    rw, rh = extra
                    pygame.draw.rect(self.surface, rgb,
                                     pygame.Rect(x + dx_ * kx, y + dy_ * ky, rw * kx, rh * ky))
                elif kind == "circle":
                    pygame.draw.circle(self.surface, rgb,
                                       (x + int(dx_ * kx), y + int(dy_ * ky)),
                                       int(extra * kx))
                elif kind == "text":
                    img = self.font_screen.render(extra, True, rgb)
                    self.surface.blit(img, (x + dx_ * kx, y + dy_ * ky))
            y += sh + 10

        # help
        y = self.surface.get_height() - 92
        for text in ("space pause   -/+ speed   d ray",
                     "b drop load bag   1-4 touchled",
                     ",/. // brain L/Check/R buttons",
                     "wasd/arrows controller sticks"):
            img = self.font_small.render(text, True, HUD_DIM)
            self.surface.blit(img, (x, y))
            y += 16
