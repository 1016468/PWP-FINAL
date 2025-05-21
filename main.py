from MotorModule import Motor
from LaneModule import getLaneCurve
from time import sleep
import WebcamModule
import utils
import sys

# Set up for completely headless operation
SIMULATION_MODE = False  # Set to False for real hardware

# Initialize motor
motor = Motor(simulation=SIMULATION_MODE)

# Initialize trackbars with fixed values that work well
# Format: [Width Top, Height Top, Width Bottom, Height Bottom]
# These values define the trapezoid for lane detection
utils.initializeTrackbars([102, 80, 20, 214])

# New: State variables for correction mode
correction_mode = False
correction_attempts = 0
MAX_CORRECTION_ATTEMPTS = 5

def main():
    global correction_mode, correction_attempts
    
    # Get image from webcam
    img = WebcamModule.getImg(display=False)
    
    # Check if image is valid
    if img is None:
        print("Warning: Failed to get camera image")
        return False
    
    # Get curve value from lane detection (disable all displays)
    curveVal = getLaneCurve(img, display=0)
    
    # Configure driving parameters
    sensitivity = 1.5     # How strongly to react to curves
    maxTurn = 0.5         # Maximum turning value
    baseSpeed = 0.35      # Forward speed
    
    # Clamp curve value to prevent too sharp turns
    curveVal = max(min(curveVal, maxTurn), -maxTurn)
    
    # Check if we need to enter correction mode
    # Enter correction mode if curve is significant
    if not correction_mode and abs(curveVal) > 0.2:
        print(f"Entering correction mode! Curve detected: {curveVal:.4f}")
        correction_mode = True
        correction_attempts = 0
        # Stop the robot first
        motor.stop(0.5)
    
    if correction_mode:
        # We're in correction mode - stop and turn until centered
        correction_attempts += 1
        
        # Determine turn direction and strength based on curve value
        # Higher curve value means sharper turn
        turn_strength = 0.8 if abs(curveVal) > 0.3 else 0.6
        
        if abs(curveVal) < 0.05:
            # We've successfully centered - exit correction mode
            print("Centered! Resuming normal driving")
            correction_mode = False
            motor.stop(0.2)  # Brief stop before resuming
            return True
        
        # Apply correction turn (no forward movement - pure turning)
        # Negative turn for positive curve (turn left if drifting right)
        turn_direction = -1 if curveVal > 0 else 1
        turn_value = turn_direction * turn_strength
        
        print(f"Correction attempt {correction_attempts}: Turning {turn_value:.2f}")
        
        # Execute a short turning movement
        motor.move(0, turn_value, 0.1)
        motor.stop(0.1)  # Brief pause between corrections
        
        # If we've tried too many times, exit correction mode anyway
        if correction_attempts >= MAX_CORRECTION_ATTEMPTS:
            print("Max correction attempts reached. Resuming normal driving")
            correction_mode = False
    
    else:
        # Normal driving mode - similar to original code
        # Fine-tuning around the center to reduce jitter
        if abs(curveVal) < 0.05:
            curveVal = 0  # Ignore very small curves (noise)
        elif abs(curveVal) > 0.15:  # Reduced from 0.2 to catch curves earlier
            # For sharp curves, increase turning response and reduce speed
            sensitivity = 1.8
            baseSpeed = 0.25  # Slow down in sharp curves for stability
        elif curveVal > 0:
            sensitivity = 1.5  # Slightly higher sensitivity for right turns
        
        # Print debug info
        print(f"Normal driving - Curve: {curveVal:.4f}, Speed: {baseSpeed:.2f}, Turn: {-curveVal * sensitivity:.4f}")
        
        # Send command to motor
        motor.move(baseSpeed, -curveVal * sensitivity, 0.05)
    
    return True

if __name__ == '__main__':
    print("Starting autonomous robot in headless mode...")
    
    # Short motor test to verify connectivity
    print("Testing motors...")
    motor.move(0.25, 0, 1)  # Move forward briefly
    motor.stop(0.5)
    print("Motor test complete")
    
    # Main control loop
    failure_count = 0
    max_failures = 5
    
    try:
        print("Beginning autonomous navigation...")
        while True:
            success = main()
            
            # Handle camera/detection failures
            if not success:
                failure_count += 1
                print(f"Operation failure {failure_count}/{max_failures}")
                
                if failure_count >= max_failures:
                    print("Too many failures. Stopping...")
                    motor.stop()
                    break
            else:
                failure_count = 0  # Reset failure counter on success
                
            sleep(0.05)  # Small delay between iterations
            
    except KeyboardInterrupt:
        print("Program stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always ensure motors are stopped when exiting
        print("Stopping motors and cleaning up...")
        motor.stop()
        sys.exit(0)
