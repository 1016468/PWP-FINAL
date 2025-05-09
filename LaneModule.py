
1016468/PWP-FINAL
main

GITHUB

This code needs to run a robot automatically does it work

I've reviewed the code for your robot, which appears to be a lane-following robot that uses computer vision and motor control. The code looks well-structured, with separate modules for lane detection, motor control, webcam input, and utility functions.

The system works by:

Capturing images from a camera
Processing the images to detect lanes
Calculating steering values based on the detected lanes
Sending commands to the motors
Based on my analysis, the code should function, but I've identified a few potential issues and improvements:

Potential Issues
Camera Detection: The WebcamModule.py tries multiple camera indices (0, 1, 2) but doesn't properly close cameras if they're found but can't capture images.
Missing Error Handling: If the camera fails to initialize or doesn't return images, the main loop might encounter issues.
Trackbar Initialization: The trackbars are initialized but there's no actual GUI component to adjust them in headless mode.
Motor Control Parameters: The motor sensitivity and speed values may need fine-tuning for your specific robot hardware.
Suggested Improvements
Let me create an artifact with an improved version of the main.py file that addresses some of these concerns:


Improved main.py
Code 
Let me also create an artifact with improvements to the WebcamModule to make camera detection more robust:


Improved WebcamModule.py
Code 
Summary of the Code and Functionality
Your robot is a lane-following autonomous vehicle that uses:

Computer Vision (OpenCV) to:
Capture images from a camera
Threshold the image to detect lane markings
Warp the perspective to get a bird's-eye view
Calculate a histogram to find the center of the lane
Motor Control to:
Control two motors separately for differential steering
Apply appropriate sensitivity and minimum power thresholds
Make smooth turns based on the detected lane curve
How The Lane Detection Works
Thresholding: Converts the image to HSV and isolates white/light gray areas (likely your lane markings)
Perspective Warping: Transforms the camera view to a bird's-eye view using predefined points
Histogram Analysis: Calculates the position of the lane by analyzing pixel intensity across the image
Curve Calculation: Determines how much the robot needs to turn based on lane position
How The Motor Control Works
The Motor class controls two motors (likely left and right wheels)
It handles differential steering (one wheel faster than the other to turn)
It applies minimum throttle values to ensure the motors have enough power to move
It has safety limits on maximum speed
Improvements I've Made
Enhanced Error Handling: Better handling of camera failures and system errors
Camera Connection Management: Caching the camera connection to improve reliability
Failure Recovery: Added counter for consecutive failures to prevent the robot from continuing with bad data
Clean Shutdown: Ensuring motors stop when the program exits
How to Test
Start with SIMULATION_MODE = True to see the motor commands without actually moving the robot
Run the improved main.py and check if lane detection and motor commands look reasonable
When ready, set SIMULATION_MODE = False to control the actual motors
Additional Notes
The lane detection parameters in utils.initializeTrackbars may need adjustment based on your specific lane width and camera position
The sensitivity and baseSpeed values in main.py will likely need fine-tuning for your specific robot
Make sure your camera is properly mounted and focused on the lane ahead
Would you like me to explain any specific part of the code in more detail or help with additional improvements?




i dont need a gui i just need the robot to move properly

You're right - for an autonomous robot, we don't need a GUI. Let me create a streamlined version that focuses solely on making the robot move properly without any GUI elements or display code.


Headless main.py
Code 
Now let's also create a streamlined headless version of the WebcamModule:


Headless WebcamModule.py
Code 
Finally, let's make sure the LaneModule is optimized for headless operation:


Optimized utils.py for headless operation
Code 
Instructions to Make Your Robot Move Properly (Headless Mode)
I've created three headless-optimized modules for your robot that focus purely on movement without any GUI elements:

Headless main.py: The main control script that initiates the robot operation
Headless WebcamModule.py: A streamlined webcam handler for capturing images
Optimized utils.py: Lane detection utilities without any display functions
Setup Instructions:
Replace your existing files with these headless versions
Set SIMULATION_MODE = False in the main.py file to control the actual motors
Check your camera position to ensure it's properly viewing the lane
Fine-Tuning for Better Performance:
Speed and Turn Sensitivity: In the main.py file, adjust these parameters:
python
sensitivity = 1.0  # Increase if turns are too gentle
maxTurn = 0.2      # Increase for sharper turns
baseSpeed = 0.15   # Increase for faster forward speed
Lane Detection Area: If the robot isn't detecting lanes properly, adjust the trapezoid dimensions:
python
utils.initializeTrackbars([102, 80, 20, 214])
The first two values define the width and height of the top of the trapezoid
The last two values define the width and height of the bottom of the trapezoid
These should be adjusted based on your specific camera mounting position
Lane Thresholding: If your lanes have different colors or lighting conditions, adjust the HSV thresholds in utils.py:
python
lowerGray = np.array([0, 0, 130])     # [Hue, Saturation, Value]
upperGray = np.array([180, 60, 255])  # Adjust for your lane color
Running the Robot:
To run the robot, execute:
python main.py
To stop the robot, press CTRL+C in the terminal.
What to Watch For:
Motor Response: The robot should move forward and make smooth turns according to the lane
Lane Detection: Check the debug output to see if curve values make sense:
Positive values indicate a right curve
Negative values indicate a left curve
Values near zero indicate straight path
Camera Connectivity: Make sure the camera is properly connected and returning images
These optimized modules focus on making your robot move properly without any GUI distractions. The code is streamlined for reliability and performance in a headless environment.

Would you like me to explain any specific aspect of the code or help with further optimization?





Error: cannot unpack non-iterable int object

This error message "cannot unpack non-iterable int object" typically occurs when you're trying to unpack values from something that's not a collection (like a tuple or list), but is instead a single integer.

Looking at your code, I can identify where this error is likely happening. Let me fix it:


Fixed LaneModule.py
Code 
Now I also need to fix the getHistogram function in utils.py to ensure it returns consistent values:


Fixed utils.py
Code 



import cv2
import numpy as np
import utils


def getLaneCurve(img, display=2):
    curveList = []
    avgVal = 10
    imgCopy = img.copy()
    imgResult = img.copy()
    #### STEP 1
    imgThres = utils.thresholding(img)

    #### STEP 2
    hT, wT, c = img.shape
    points = utils.valTrackbars()
    imgWarp = utils.warpImg(imgThres, points, wT, hT)
    imgWarpPoints = utils.drawPoints(imgCopy, points)

    #### STEP 3
    # Fix for the histogram function - handle return values correctly
    if utils.HEADLESS or display == 0:
        middlePoint = utils.getHistogram(imgWarp, display=False, minPer=0.5, region=4)
        curveAveragePoint = utils.getHistogram(imgWarp, display=False, minPer=0.9)
    else:
        middlePoint, imgHist = utils.getHistogram(imgWarp, display=True, minPer=0.5, region=4)
        curveAveragePoint, imgHist = utils.getHistogram(imgWarp, display=True, minPer=0.9)
    
    curveRaw = curveAveragePoint - middlePoint

    #### SETP 4
    curveList.append(curveRaw)
    if len(curveList) > avgVal:
        curveList.pop(0)
    curve = int(sum(curveList) / len(curveList))

    #### STEP 5
    if display != 0 and not utils.HEADLESS:
        imgInvWarp = utils.warpImg(imgWarp, points, wT, hT, inv=True)
        imgInvWarp = cv2.cvtColor(imgInvWarp, cv2.COLOR_GRAY2BGR)
        imgInvWarp[0:hT // 3, 0:wT] = 0, 0, 0
        imgLaneColor = np.zeros_like(img)
        imgLaneColor[:] = 0, 255, 0
        imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)
        imgResult = cv2.addWeighted(imgResult, 1, imgLaneColor, 1, 0)
        midY = 450
        cv2.putText(imgResult, str(curve), (wT // 2 - 80, 85), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
        cv2.line(imgResult, (wT // 2, midY), (wT // 2 + (curve * 3), midY), (255, 0, 255), 5)
        cv2.line(imgResult, ((wT // 2 + (curve * 3)), midY - 25), (wT // 2 + (curve * 3), midY + 25), (0, 255, 0), 5)
        for x in range(-30, 30):
            w = wT // 20
            cv2.line(imgResult, (w * x + int(curve // 50), midY - 10),
                     (w * x + int(curve // 50), midY + 10), (0, 0, 255), 2)
        
        if display == 2:
            imgStacked = utils.stackImages(0.7, ([img, imgWarpPoints, imgWarp],
                                             [imgHist, imgLaneColor, imgResult]))
            cv2.imshow('ImageStack', imgStacked)
        elif display == 1:
            cv2.imshow('Result', imgResult)

    #### NORMALIZATION
    curve = curve / 100
    if curve > 1:
        curve = 1
    if curve < -1:
        curve = -1

    return curve

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        if success:
            curve = getLaneCurve(img, display=1)
            print(curve)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
