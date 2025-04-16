from MotorModule import Motor
from LaneModule import getLaneCurve
import WebcamModule

# Initialize the motor (no need for GPIO pins now)
motor = Motor()

def main():
    img = WebcamModule.getImg()
    curveVal = getLaneCurve(img, 1)

    # Tweakable driving sensitivity + speed limit
    sen = 1.3
    maxVal = 0.3

    # Clamp curveVal within range
    if curveVal > maxVal:
        curveVal = maxVal
    if curveVal < -maxVal:
        curveVal = -maxVal

    # Chill the steering near the center
    if curveVal > 0:
        sen = 1.7
        if curveVal < 0.05:
            curveVal = 0
    else:
        if curveVal > -0.08:
            curveVal = 0

    # Move with speed and turn control
    motor.move(0.20, -curveVal * sen, 0.05)

if __name__ == '__main__':
    while True:
        main()
