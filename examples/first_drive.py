#region VEXcode Generated Robot Configuration
from vex import *
import urandom

# Brain should be defined by default
brain = Brain()

# Robot configuration code
brain_inertial = Inertial()
left_drive_smart = Motor(Ports.PORT1, True)
right_drive_smart = Motor(Ports.PORT2, False)

drivetrain = SmartDrive(left_drive_smart, right_drive_smart, brain_inertial, 200, 173, 76, MM, 1)
intake_motor = Motor(Ports.PORT6, False)
arm_motor = Motor(Ports.PORT10, False)
bumper_front = Bumper(Ports.PORT3)
distance_front = Distance(Ports.PORT4)

vexcode_initial_drivetrain_calibration_completed = False
def calibrate_drivetrain():
    # Calibrate the Drivetrain Inertial
    global vexcode_initial_drivetrain_calibration_completed
    sleep(200, MSEC)
    brain.screen.print("Calibrating")
    brain.screen.next_row()
    brain.screen.print("Inertial")
    brain_inertial.calibrate()
    while brain_inertial.is_calibrating():
        sleep(25, MSEC)
    vexcode_initial_drivetrain_calibration_completed = True
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)

calibrate_drivetrain()
#endregion VEXcode Generated Robot Configuration

# Begin project code

brain.screen.print("Driving a square!")

drivetrain.set_drive_velocity(60, PERCENT)
drivetrain.set_turn_velocity(40, PERCENT)
drivetrain.set_timeout(5, SECONDS)  # don't stall forever if we hit something

# Turn LEFT: a right-hand square from the start zone runs into the yellow
# field wall at x=60. Legs are 250 mm so the second corner clears the
# L4 octagon goal at (36.5, 30.5).
for side in range(4):
    drivetrain.drive_for(FORWARD, 250, MM)
    drivetrain.turn_for(LEFT, 90, DEGREES)

brain.screen.next_row()
brain.screen.print("Done. Heading:", brain_inertial.heading())
