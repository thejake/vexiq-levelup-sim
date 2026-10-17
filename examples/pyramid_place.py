# MECHANICS DEMO (not a competition routine): shows how pyramid placement
# works — drive to the pyramid, raise the arm, eject. Scores the yellow
# preload on the red pyramid's L3 (12 pts). Design your own auton!
#
# The L3 shelf is deep inside the pyramid, so the arm must lift the bag
# high (~10") — in the sim the drop point also reaches forward as the arm
# rises, like a real four-bar lift.

#region VEXcode Generated Robot Configuration
from vex import *
import urandom

brain = Brain()
brain_inertial = Inertial()
left_drive_smart = Motor(Ports.PORT1, True)
right_drive_smart = Motor(Ports.PORT2, False)
drivetrain = SmartDrive(left_drive_smart, right_drive_smart, brain_inertial, 200, 173, 76, MM, 1)
intake_motor = Motor(Ports.PORT6, False)
arm_motor = Motor(Ports.PORT10, False)

def calibrate_drivetrain():
    sleep(200, MSEC)
    brain_inertial.calibrate()
    while brain_inertial.is_calibrating():
        sleep(25, MSEC)

calibrate_drivetrain()
#endregion VEXcode Generated Robot Configuration

# Begin project code

drivetrain.set_drive_velocity(60, PERCENT)
drivetrain.set_turn_velocity(35, PERCENT)
# The timeout must be LONGER than your longest leg (43" at 60% is ~5s),
# or drive_for gives up early and every later move starts from the wrong
# place. We shorten it later just for the wall-press.
drivetrain.set_timeout(8, SECONDS)
arm_motor.set_velocity(80, PERCENT)
intake_motor.set_velocity(100, PERCENT)

brain.screen.print("Preload to L3!")

# The elevated beam blocks mid-field at x=60 below y~44, so take the top
# lane across, then come DOWN onto the pyramid from above.
drivetrain.drive_for(FORWARD, 43, INCHES)      # up-field to y ~= 52
drivetrain.turn_to_heading(90, DEGREES)        # face the red end
drivetrain.drive_for(FORWARD, 41, INCHES)      # across the top to x ~= 89.5
# (stop short of the wall: a turn in place sweeps the robot's corners
#  out to its half-DIAGONAL, ~7", so leave that much clearance)
drivetrain.turn_to_heading(180, DEGREES)       # face the pyramid (down-field)
drivetrain.drive_for(FORWARD, 26, INCHES)      # approach the footprint

# Raise the arm while squaring up against the pyramid base.
arm_motor.spin_to_position(400, DEGREES, wait=False)
drivetrain.set_timeout(2, SECONDS)
drivetrain.drive_for(FORWARD, 4, INCHES)       # press the base; timeout ends it
while not arm_motor.is_done():
    wait(20, MSEC)

# Drop the bag onto L3 and back away.
intake_motor.spin(REVERSE)
wait(600, MSEC)
intake_motor.stop()
drivetrain.drive_for(REVERSE, 8, INCHES)
arm_motor.spin_to_position(0, DEGREES)

brain.screen.next_row()
brain.screen.print("12 points?")
