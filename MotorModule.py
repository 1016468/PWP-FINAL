from adafruit_motorkit import MotorKit
import board
from time import sleep

class Motor:
    def __init__(self, simulation=True):
        self.simulation = simulation
        if not simulation:
            try:
                self.kit = MotorKit(address=0x40)  # Default I2C setup for Pi
                # Initialize motors to stopped state
                self.kit.motor1.throttle = 0
                self.kit.motor2.throttle = 0
                print("Motors initialized successfully")
            except Exception as e:
                print(f"Motor initialization error: {e}")
                print("Make sure I2C is enabled on your Raspberry Pi")
                self.simulation = True  # Fallback to simulation
        self.mySpeed = 0
        
        # Define minimum throttle value for good movement
        self.MIN_THROTTLE = 0.7  # This is 70% of max power (equivalent to 7 on a 0-10 scale)
    
    def move(self, speed=0.5, turn=0, t=0):
        # Apply base speed scaling
        base_speed = 1.0  # Full range is -1.0 to 1.0 for Adafruit
        speed *= base_speed
        turn *= 0.7
        
        # Calculate left and right motor speeds
        leftSpeed = speed - turn
        rightSpeed = speed + turn
        
        # Apply minimum throttle while preserving direction
        if leftSpeed > 0 and leftSpeed < self.MIN_THROTTLE:
            leftSpeed = self.MIN_THROTTLE
        elif leftSpeed < 0 and leftSpeed > -self.MIN_THROTTLE:
            leftSpeed = -self.MIN_THROTTLE
            
        if rightSpeed > 0 and rightSpeed < self.MIN_THROTTLE:
            rightSpeed = self.MIN_THROTTLE
        elif rightSpeed < 0 and rightSpeed > -self.MIN_THROTTLE:
            rightSpeed = -self.MIN_THROTTLE
        
        # When speed is very low or zero (for turning in place), don't apply minimum
        if abs(speed) < 0.1:
            # For pure turning, we'll use smaller values
            leftSpeed = turn * 0.7
            rightSpeed = -turn * 0.7
        
        # Clamp the values between -0.8 and 0.8 (for safety)
        leftSpeed = max(min(leftSpeed, 0.8), -0.8)
        rightSpeed = max(min(rightSpeed, 0.8), -0.8)
        
        # Debug output and motor control
        if self.simulation:
            print(f"Motors: Left={leftSpeed:.2f}, Right={rightSpeed:.2f}")
        else:
            # Add negative signs to reverse the motor direction
            self.kit.motor1.throttle = -leftSpeed
            self.kit.motor2.throttle = -rightSpeed
        
        sleep(t)
    
    def stop(self, t=0):
        if not self.simulation:
            self.kit.motor1.throttle = 0
            self.kit.motor2.throttle = 0
        else:
            print("Motors: Left=0.00, Right=0.00")
        self.mySpeed = 0
        sleep(t)

if __name__ == '__main__':
    motor = Motor(simulation=True)
    print("Testing forward movement")
    motor.move(0.5, 0, 2)  # Forward
    motor.stop(1)
    
    print("Testing backward movement")
    motor.move(-0.5, 0, 2)  # Backward
    motor.stop(1)
    
    print("Testing right turn")
    motor.move(0, 0.5, 2)  # Turn right
    motor.stop(1)
    
    print("Testing left turn")
    motor.move(0, -0.5, 2)  # Turn left
    motor.stop(1)
    
    print("Testing forward with right curve")
    motor.move(0.5, 0.3, 2)  # Forward with right curve
    motor.stop(1)
