# Skills-style opener: drive the yellow preload into the red floor goal,
# using the distance sensor to stop near the wall. The robot starts in the
# start zone facing +Y with a yellow bag already in the intake.

#region VEXcode Generated Robot Configuration
from vex import *
import urandom

brain = Brain()
brain_inertial = Inertial()
left_drive_smart = Motor(Ports.PORT1, True)
right_drive_smart = Motor(Ports.PORT2, False)
drivetrain = SmartDrive(left_drive_smart, right_drive_smart, brain_inertial, 200, 173, 76, MM, 1)
intake_motor = Motor(Ports.PORT6, False)
distance_front = Distance(Ports.PORT4)

def calibrate_drivetrain():
    sleep(200, MSEC)
    brain_inertial.calibrate()
    while brain_inertial.is_calibrating():
        sleep(25, MSEC)

calibrate_drivetrain()
#endregion VEXcode Generated Robot Configuration

# Begin project code

drivetrain.set_drive_velocity(50, PERCENT)
drivetrain.set_turn_velocity(35, PERCENT)
drivetrain.set_timeout(6, SECONDS)
intake_motor.set_velocity(100, PERCENT)

brain.screen.print("To the red goal")

# The yellow wall (x=60, up to y=26.5), its floor barrier (to y=39) and the
# L4 octagon block the middle of the field. The open lane to the red end is
# along the top, so drive up-field first, then turn right.
drivetrain.drive_for(FORWARD, 43, INCHES)   # start zone to y ~= 52
drivetrain.turn_to_heading(90, DEGREES)     # 90 cw from start = facing +X

# Drive until the distance sensor sees the red-end perimeter up close.
drivetrain.drive(FORWARD)
while distance_front.object_distance(MM) > 350:
    wait(20, MSEC)
drivetrain.stop()

# Nose over the goal line and eject the bag.
drivetrain.drive_for(FORWARD, 9, INCHES)
intake_motor.spin(REVERSE)
wait(1, SECONDS)
intake_motor.stop()

# Back out of the goal.
drivetrain.drive_for(REVERSE, 12, INCHES)

brain.screen.print("Red goal:", "scored!" )
