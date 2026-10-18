# DRIVE MANUALLY with the keyboard. Click the sim window first so it has
# focus, then:
#
#   w / s          drive forward / backward   (left stick, axisA)
#   left / right   turn                       (right stick, axisC)
#   n / m          intake in / out            (buttonRUp / buttonRDown)
#   r / f          arm up / down              (buttonEUp / buttonEDown)
#   p              print the robot's pose to the terminal (sim-only key)
#
# This is a normal VEX IQ driver-control program: it reads the controller
# in a loop and feeds the drivetrain motors. On the real robot the same
# code drives from the real controller's joysticks. The sim keyboard just
# pretends to be that controller.

#region VEXcode Generated Robot Configuration
from vex import *
import urandom

brain = Brain()
controller = Controller()
brain_inertial = Inertial()
left_drive_smart = Motor(Ports.PORT1, True)
right_drive_smart = Motor(Ports.PORT2, False)
# The SmartDrive tells the sim which motors are the wheels; in this program
# we then drive those two motors directly (that's how VEXcode driver
# control works too).
drivetrain = SmartDrive(left_drive_smart, right_drive_smart, brain_inertial, 200, 173, 76, MM, 1)
intake_motor = Motor(Ports.PORT6, False)
arm_motor = Motor(Ports.PORT10, False)
#endregion VEXcode Generated Robot Configuration

# Begin project code

brain.screen.print("Drive me! (w/s + arrows)")

arm_motor.set_stopping(HOLD)      # don't let the arm sag when released
arm_motor.set_velocity(60, PERCENT)
intake_motor.set_velocity(100, PERCENT)

DEADBAND = 5  # ignore tiny stick values so the robot sits still untouched

while True:
    # Split-arcade: one stick for speed, the other for turning.
    forward = controller.axisA.position()   # w = +100, s = -100
    turn = controller.axisC.position()      # right arrow = +100

    if abs(forward) < DEADBAND:
        forward = 0
    if abs(turn) < DEADBAND:
        turn = 0

    # Mix speed and turn into per-side wheel velocities. A negative
    # velocity with spin(FORWARD) runs the motor backward (same as the
    # real robot), so one pair of lines covers every direction.
    left_drive_smart.set_velocity(forward + turn, PERCENT)
    right_drive_smart.set_velocity(forward - turn, PERCENT)
    left_drive_smart.spin(FORWARD)
    right_drive_smart.spin(FORWARD)

    if controller.buttonRUp.pressing():       # n
        intake_motor.spin(FORWARD)
    elif controller.buttonRDown.pressing():   # m
        intake_motor.spin(REVERSE)
    else:
        intake_motor.stop()

    if controller.buttonEUp.pressing():       # r
        arm_motor.spin(FORWARD)
    elif controller.buttonEDown.pressing():   # f
        arm_motor.spin(REVERSE)
    else:
        arm_motor.stop()

    wait(20, MSEC)
