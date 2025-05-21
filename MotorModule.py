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
        
        # Define minimum throttle value needed for motors to actually move
        self.MIN_THROTTLE = 0.7  # Motors need at least 70% power to move
        
        # Left motor is much stronger than right motor - apply compensation
        self.LEFT_MOTOR_FACTOR = 0.65  # Reduce left motor power by 35%
        self.RIGHT_MOTOR_FACTOR = 1.0  # Keep right motor at full power
    
    def move(self, speed=0.8, turn=0, t=0):
        # Apply base speed scaling
        base_speed = 1.0  # Full range is -1.0 to 1.0 for Adafruit
        speed *= base_speed
        
        # Increased turn factor for sharper turns
        turn *= 0.71  # Keeps original turn sensitivity
        
        # Calculate left and right motor speeds
        leftSpeed = speed - turn
        rightSpeed = speed + turn
        
        # Apply motor compensation - left motor is stronger so we reduce its power
        leftSpeed *= self.LEFT_MOTOR_FACTOR
        rightSpeed *= self.RIGHT_MOTOR_FACTOR
        
        # Apply minimum throttle while preserving direction
        if leftSpeed > 0 and leftSpeed < self.MIN_THROTTLE:
            leftSpeed = self.MIN_THROTTLE * self.LEFT_MOTOR_FACTOR  # Apply factor to minimum too
        elif leftSpeed < 0 and leftSpeed > -self.MIN_THROTTLE:
            leftSpeed = -self.MIN_THROTTLE * self.LEFT_MOTOR_FACTOR  # Apply factor to minimum too
            
        if rightSpeed > 0 and rightSpeed < self.MIN_THROTTLE:
            rightSpeed = self.MIN_THROTTLE
        elif rightSpeed < 0 and rightSpeed > -self.MIN_THROTTLE:
            rightSpeed = -self.MIN_THROTTLE
        
        # Improve pivot turning for sharp turns
        if abs(speed) < 0.1:
            # For pure turning, balance motors for straighter turning
            # Reduce left motor power even during turns
            if turn > 0:  # Turning right - left motor forward, right motor backward
                leftSpeed = turn * self.MIN_THROTTLE * 1.2 * self.LEFT_MOTOR_FACTOR
                rightSpeed = -turn * self.MIN_THROTTLE * 1.2
            else:  # Turning left - left motor backward, right motor forward
                # For left turns, we need to apply more power to right and less to left
                leftSpeed = turn * self.MIN_THROTTLE * 1.2 * self.LEFT_MOTOR_FACTOR
                rightSpeed = -turn * self.MIN_THROTTLE * 1.2
        
        # Apply speed limits
        leftSpeed = max(min(leftSpeed, 1.0), -1.0)
        rightSpeed = max(min(rightSpeed, 1.0), -1.0)
        
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
    motor.move(0.9, 0, 2)  # Forward with high speed (exceeds 0.75 minimum)
    motor.stop(1)
    
    print("Testing backward movement")
    motor.move(-0.9, 0, 2)  # Backward with high speed
    motor.stop(1)
    
    print("Testing right turn")
    motor.move(0, 0.9, 2)  # Sharper right turn with high power
    motor.stop(1)
    
    print("Testing left turn")
    motor.move(0, -0.9, 2)  # Sharper left turn with high power
    motor.stop(1)
    
    print("Testing forward with right curve")
    motor.move(0.9, 0.5, 2)  # Forward with sharper right curve at high speed
    motor.stop(1)
