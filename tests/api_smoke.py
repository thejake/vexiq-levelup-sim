# Broad API smoke test: exercises most of the fake vex surface.
from vex import *

brain = Brain()
bi = Inertial()
lm = Motor(Ports.PORT1, 1.5, True)   # float gear ratio form
rm = Motor(Ports.PORT2, False)       # bool-as-arg2 form
m3 = Motor(Ports.PORT7)              # bare form
g = MotorGroup(lm, rm)
dt = SmartDrive(lm, rm, bi, 200, 173, 76, MM, 1)
tl = Touchled(Ports.PORT5)
opt = Optical(Ports.PORT8)
bump = Bumper(Ports.PORT3)
dist = Distance(Ports.PORT4)
ctrl = Controller()

assert m3.gear_ratio == 1.0 and lm.gear_ratio == 1.5 and lm.reversed
bi.calibrate()
assert not bi.is_calibrating()

# motor position moves
m3.set_velocity(50, PERCENT)
m3.spin_for(FORWARD, 360, DEGREES)
p = m3.position(DEGREES)
assert 355 < p < 365, p
m3.spin_to_position(0, DEGREES)
assert abs(m3.position(DEGREES)) < 5
m3.spin_for(REVERSE, 1, TURNS, wait=False)
wait(100, MSEC)
assert m3.is_spinning()
while not m3.is_done():
    wait(20, MSEC)
assert abs(m3.position(DEGREES) + 360) < 10, m3.position()

# timer
t = Timer()
wait(250, MSEC)
assert 200 < t.time(MSEC) < 320, t.time(MSEC)
assert 0.2 < t.time(SECONDS) < 0.33

# events and threads
hits = []
ev = Event()
ev(lambda: hits.append("a"))
ev(lambda n: hits.append(n), ("b",))
ev.broadcast_and_wait()
assert sorted(hits) == ["a", "b"], hits

flag = []
th = Thread(lambda: flag.append(1))
wait(100, MSEC)
assert flag == [1]

# touchled
tl.set_color(Color.RED)
assert tl.color_rgb == (255, 0, 0)
tl.off()

# brain screen
brain.screen.set_cursor(1, 1)
brain.screen.print("row one", 1.2345, precision=3)
brain.screen.next_row()
brain.screen.print("row two")
rows, draws = brain.screen.snapshot()
assert rows[0].startswith("row one 1.234"), rows[0]
assert rows[1] == "row two"
brain.screen.draw_circle(80, 54, 10)
brain.screen.draw_line(0, 0, 159, 107)

# heading / turns via drivetrain
dt.set_turn_velocity(50, PERCENT)
dt.turn_to_heading(45, DEGREES)
h = bi.heading()
assert 42 < h < 48, h
dt.set_heading(0, DEGREES)
assert dt.heading() < 2 or dt.heading() > 358

# distance: facing +Y from start after set_heading trickery — just sanity
d = dist.object_distance(MM)
assert 20 <= d <= 2000, d
assert isinstance(dist.is_object_detected(), bool)

# bumper not pressed in open field
assert bump.pressing() == 0
# controller neutral
assert ctrl.axisA.position() == 0 and not ctrl.buttonLUp.pressing()

# unimplemented things raise loudly
try:
    Pneumatic(Ports.PORT9)
    raise AssertionError("Pneumatic should raise")
except Exception as e:
    assert "not implemented" in str(e)

print("API SMOKE: ALL PASS")
