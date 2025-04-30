from adafruit_motorkit import MotorKit
import board
from time import sleep

class Motor:
    def __init__(self, simulation=True):
        self.simulation = simulation
        if not simulation:
            try:
                self.kit = MotorKit(address=0x40)  # Default I2C setup for Pi
            except Exception as e:
                print(f"Motor initialization error: {e}")
                print("Make sure I2C is enabled on your Raspberry Pi")
                self.simulation = True  # Fallback to simulation
        self.mySpeed = 0

    def move(self, speed=0.5, turn=0, t=0):
        speed *= 1.0  # Full range is -1.0 to 1.0 for Adafruit
        turn *= 0.7

        leftSpeed = speed - turn
        rightSpeed = speed + turn

        # Clamp the values between -1.0 and 1.0
        leftSpeed = max(min(leftSpeed, 0.8), -0.8)
        rightSpeed = max(min(rightSpeed, 0.8), -0.8)

        if self.simulation:
            print(f"Motors: Left={leftSpeed:.2f}, Right={rightSpeed:.2f}")
        else:
            self.kit.motor1.throttle = leftSpeed
            self.kit.motor2.throttle = rightSpeed
        sleep(t)

    def stop(self, t=0):
        self.kit.motor1.throttle = 0
        self.kit.motor2.throttle = 0
        self.mySpeed = 0
        sleep(t)

if __name__ == '__main__':
    motor = Motor(simulation=True)
    motor.move(0.5, 0, 2)  # Forward
    motor.stop(2)

    motor.move(-0.5, 0, 2)  # Backward
    motor.stop(2)

    motor.move(0, 0.5, 2)  # Turn right
    motor.stop(2)

    motor.move(0, -0.5, 2)  # Turn left
    motor.stop(2)