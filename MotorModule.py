from adafruit_motorkit import MotorKit
from time import sleep

class Motor:
    def __init__(self):
        self.kit = MotorKit(0x40)
        self.mySpeed = 0

    def move(self, speed=0.5, turn=0, t=0):
        speed *= 1.0  # Full range is -1.0 to 1.0 for Adafruit
        turn *= 0.7

        leftSpeed = speed - turn
        rightSpeed = speed + turn

        # Clamp the values between -1.0 and 1.0
        leftSpeed = max(min(leftSpeed, 1.0), -1.0)
        rightSpeed = max(min(rightSpeed, 1.0), -1.0)

        self.kit.motor1.throttle = leftSpeed
        self.kit.motor3.throttle = rightSpeed
        sleep(t)

    def stop(self, t=0):
        self.kit.motor1.throttle = 0
        self.kit.motor3.throttle = 0
        self.mySpeed = 0
        sleep(t)

def main():
    motor.move(0.5, 0, 2)  # Forward
    motor.stop(2)

    motor.move(-0.5, 0, 2)  # Backward
    motor.stop(2)

    motor.move(0, 0.5, 2)  # Turn right
    motor.stop(2)

    motor.move(0, -0.5, 2)  # Turn left
    motor.stop(2)
