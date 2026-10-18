"""Simulator runner: `python -m vexsim path/to/program.py [options]`.

Main thread: pygame window + physics stepping (macOS requires the display
on the main thread). User program: a daemon worker thread whose blocking
VEX calls wait on the sim clock.
"""

from __future__ import annotations

import argparse
import json
import os
import runpy
import sys
import threading
import traceback


def main() -> None:
    parser = argparse.ArgumentParser(prog="vexsim")
    parser.add_argument("script", help="VEX IQ Python program to run")
    parser.add_argument("--speed", type=float, default=None, help="sim speed multiplier")
    parser.add_argument("--scale", type=int, default=None, help="pixels per inch")
    parser.add_argument("--headless", action="store_true", help="no window (testing)")
    parser.add_argument("--max-sim-seconds", type=float, default=None,
                        help="stop after this much sim time")
    parser.add_argument("--screenshot", default=None, help="save a PNG on exit")
    parser.add_argument("--dump-state", default=None, help="write final world state JSON")
    args = parser.parse_args()

    script = os.path.abspath(args.script)
    if not os.path.isfile(script):
        parser.error(f"no such file: {script}")

    os.environ["VEXSIM_ACTIVE"] = "1"
    if args.headless:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    from . import runtime
    from .clock import SimClock
    from .config import load_config
    from .world import World

    config = load_config(script)
    if args.speed is not None:
        config.speed = args.speed
    if args.scale is not None:
        config.pixels_per_inch = args.scale

    clock = SimClock()
    world = World(clock, config)
    runtime.clock = clock
    runtime.world = world
    runtime.config = config

    import pygame
    pygame.init()
    from .render import Renderer
    renderer = Renderer(world, config.pixels_per_inch)

    # ---- user program thread ----

    def run_user():
        from .clock import SimShutdown
        sys.path.insert(0, os.path.dirname(script))
        try:
            runpy.run_path(script, run_name="__main__")
            world.program_status = "finished"
        except SimShutdown:
            return  # simulator is exiting; say nothing
        except SystemExit:
            world.program_status = "stopped" if world.program_stop_requested else "finished"
        except BaseException:
            traceback.print_exc()
            world.program_status = "ERROR — see terminal"
        print(f"[vexsim] program {world.program_status} at t={clock.now():.2f}s "
              "(window stays open; close it or Ctrl-C to quit)")

    user_thread = threading.Thread(target=run_user, daemon=True, name="user-program")
    user_thread.start()

    # ---- main loop ----

    speed = config.speed
    paused = False
    wall = pygame.time.Clock()
    running = True

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                        speed = min(speed * 2, 16.0)
                    elif event.key == pygame.K_MINUS:
                        speed = max(speed / 2, 0.25)
                    elif event.key == pygame.K_v:
                        # ('d' belongs to the controller left stick)
                        renderer.show_ray = not renderer.show_ray
                    elif event.key == pygame.K_b:
                        world.add_load_bag()
                    elif event.key == pygame.K_p:
                        with world._lock:
                            px, py = world.x, world.y
                            hd = (world._theta0 - world.theta) % 360
                        print(f"[vexsim] pose: x {px:.1f} y {py:.1f} in | "
                              f"x {px * 25.4:.0f} y {py * 25.4:.0f} mm | "
                              f"heading {hd:.1f} deg")
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            _read_inputs(pygame, world)

            if not paused:
                dt = (1 / 60.0) * speed
                world.step(dt)
                clock.advance(dt)

            renderer.draw(clock.now(), speed, paused)
            # Throttle even headless runs: an unthrottled loop can starve the
            # user-program thread of the GIL/clock lock.
            wall.tick(60 if not args.headless else 480)

            if args.max_sim_seconds is not None and clock.now() >= args.max_sim_seconds:
                running = False
    except KeyboardInterrupt:
        pass
    finally:
        if args.screenshot:
            pygame.image.save(renderer.surface, args.screenshot)
            print(f"[vexsim] screenshot -> {args.screenshot}")
        if args.dump_state:
            _dump_state(world, clock, args.dump_state)
        clock.shutdown()
        pygame.quit()


# keyboard -> controller / brain buttons / touchleds
_AXIS_KEYS = None


def _read_inputs(pygame, world) -> None:
    keys = pygame.key.get_pressed()

    def axis(neg, pos):
        return (100 if keys[pos] else 0) + (-100 if keys[neg] else 0)

    inp = world.input
    inp.axes["A"] = axis(pygame.K_s, pygame.K_w)       # left stick vertical
    inp.axes["B"] = axis(pygame.K_a, pygame.K_d)       # left stick horizontal
    inp.axes["C"] = axis(pygame.K_LEFT, pygame.K_RIGHT)  # right stick horizontal
    inp.axes["D"] = axis(pygame.K_DOWN, pygame.K_UP)     # right stick vertical

    inp.buttons = {
        "EUp": keys[pygame.K_r], "EDown": keys[pygame.K_f],
        "FUp": keys[pygame.K_t], "FDown": keys[pygame.K_g],
        "LUp": keys[pygame.K_z], "LDown": keys[pygame.K_x],
        "RUp": keys[pygame.K_n], "RDown": keys[pygame.K_m],
        "L3": False, "R3": False,
    }
    inp.brain_buttons = {
        "left": keys[pygame.K_COMMA],
        "check": keys[pygame.K_PERIOD],
        "right": keys[pygame.K_SLASH],
    }
    inp.touchleds = {i for i, key in enumerate(
        (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4)) if keys[key]}


def _dump_state(world, clock, path: str) -> None:
    with world._lock:
        pose = {"x": world.x, "y": world.y,
                "heading_cw": (world._theta0 - world.theta) % 360}
    state = {
        "sim_time": clock.now(),
        "pose": pose,
        "score": world.score,
        "program_status": world.program_status,
        "carrying": world.carried.color if world.carried else None,
        "bags": [{"color": b.color, "x": round(b.x, 2), "y": round(b.y, 2),
                  "carried": b.carried} for b in world.bags],
    }
    with open(path, "w") as f:
        json.dump(state, f, indent=2)
    print(f"[vexsim] state -> {path}")


if __name__ == "__main__":
    main()
