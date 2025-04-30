from MotorModule import Motor
from LaneModule import getLaneCurve
from time import sleep
import WebcamModule
import utils
import cv2

# Initialize motor and trackbars (in simulation mode)
motor = Motor(simulation=False)
utils.initializeTrackbars([102, 80, 20, 214])

def main():
    img = WebcamModule.getImg(display=False)
    curveVal = getLaneCurve(img, display=0)  # Disable display in simulation mode

    # Driving sensitivity & limits
    sensitivity = 1.0  # Reduced from 1.3
    maxTurn = 0.2     # Reduced from 0.3

    # Clamp curveVal
    curveVal = max(min(curveVal, maxTurn), -maxTurn)

    # Fine-tuning around the center
    if curveVal > 0:
        sensitivity = 1.3  # Reduced from 1.7
        if curveVal < 0.05:
            curveVal = 0
    elif curveVal > -0.08:
        curveVal = 0

    # Send command to motor
    motor.move(0.15, -curveVal * sensitivity, 0.05)  # Reduced base speed from 0.20 to 0.15

if __name__ == '__main__':
    while True:
        try:
            main()
            sleep(0.1)  # Small delay to prevent overwhelming the motor
        except KeyboardInterrupt:
            motor.stop()
            break
        except Exception as e:
            print(f"Error: {e}")
            motor.stop()
            break
