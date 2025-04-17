from MotorModule import Motor
from LaneModule import getLaneCurve
import WebcamModule
import utlis
import cv2

# Initialize motor and trackbars
motor = Motor()
utlis.initializeTrackbars([102, 80, 20, 214])

def main():
    img = WebcamModule.getImg()
    curveVal = getLaneCurve(img, display=1)

    # Driving sensitivity & limits
    sensitivity = 1.3
    maxTurn = 0.3

    # Clamp curveVal
    curveVal = max(min(curveVal, maxTurn), -maxTurn)

    # Fine-tuning around the center
    if curveVal > 0:
        sensitivity = 1.7
        if curveVal < 0.05:
            curveVal = 0
    elif curveVal > -0.08:
        curveVal = 0

    # Send command to motor
    motor.move(0.20, -curveVal * sensitivity, 0.05)

if __name__ == '__main__':
    while True:
        main()
