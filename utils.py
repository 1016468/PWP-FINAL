import os
import cv2
import numpy as np

# Force headless mode
HEADLESS = True

def thresholding(img):
    """Convert image to binary threshold to isolate lane markings"""
    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Adjusted gray-white range for better detection of light-colored lanes
    lowerGray = np.array([0, 0, 120])     # Lowered Value threshold from 130 to 120
    upperGray = np.array([180, 70, 255])  # Increased Saturation threshold from 60 to 70
    maskWhite = cv2.inRange(imgHsv, lowerGray, upperGray)
    return maskWhite

def warpImg(img, points, w, h, inv=False):
    """Apply perspective transform to get bird's eye view of lane"""
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    if inv:
        matrix = cv2.getPerspectiveTransform(pts2, pts1)
    else:
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWarp = cv2.warpPerspective(img, matrix, (w, h))
    return imgWarp

# Global variable to store trackbar values
trackbarValues = {}

def initializeTrackbars(initialTracbarVals, wT=480, hT=240):
    """Initialize fixed values for the warping trapezoid - no GUI elements"""
    global trackbarValues
    trackbarValues = {
        "Width Top": initialTracbarVals[0],
        "Height Top": initialTracbarVals[1],
        "Width Bottom": initialTracbarVals[2],
        "Height Bottom": initialTracbarVals[3]
    }

def valTrackbars(wT=480, hT=240):
    """Return the four corner points for the perspective transform"""
    global trackbarValues
    if not trackbarValues:
        # Default values if not initialized
        return np.float32([(60, 60), (wT - 60, 60), (20, 180), (wT - 20, 180)])
    
    widthTop = trackbarValues["Width Top"]
    heightTop = trackbarValues["Height Top"]
    widthBottom = trackbarValues["Width Bottom"]
    heightBottom = trackbarValues["Height Bottom"]
    
    # These points define a trapezoid that will be transformed to a rectangle
    points = np.float32([(widthTop, heightTop), (wT - widthTop, heightTop),
                       (widthBottom, heightBottom), (wT - widthBottom, heightBottom)])
    return points

def drawPoints(img, points):
    """For debugging only: Draw the trapezoid points on the image"""
    if HEADLESS:
        return img  # Skip in headless mode
        
    for x in range(4):
        cv2.circle(img, (int(points[x][0]), int(points[x][1])), 15, (0, 0, 255), cv2.FILLED)
    return img

def getHistogram(img, minPer=0.1, display=False, region=1):
    """Calculate histogram to find the center of the lane"""
    if region == 1:
        histValues = np.sum(img, axis=0)
    else:
        histValues = np.sum(img[img.shape[0] // region:, :], axis=0)

    maxValue = np.max(histValues)
    if maxValue == 0:  # Handle case where image is all black
        basePoint = img.shape[1] // 2  # Default to middle
    else:
        # Reduced minPer for better detection of faint lanes
        # This will help detect 90 degree turns more effectively
        adjustedMinPer = minPer * 0.9  
        minValue = adjustedMinPer * maxValue
        indexArray = np.where(histValues >= minValue)
        # Make sure indexArray is not empty
        if len(indexArray[0]) > 0:
            basePoint = int(np.average(indexArray[0]))
        else:
            basePoint = img.shape[1] // 2  # Default to middle if no peaks found

    if display and not HEADLESS:
        imgHist = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
        for x, intensity in enumerate(histValues):
            if intensity > 0:  # Only draw non-zero values
                height = min(int(intensity // 255 // region), img.shape[0])
                cv2.line(imgHist, (x, img.shape[0]), (x, img.shape[0] - height), (255, 0, 255), 1)
        cv2.circle(imgHist, (basePoint, img.shape[0]), 20, (0, 255, 255), cv2.FILLED)
        return basePoint, imgHist

    return basePoint

def stackImages(scale, imgArray):
    """Stack images for display - not used in headless mode"""
    if HEADLESS:
        return np.zeros((10, 10, 3), np.uint8)  # Return dummy image in headless mode
        
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]),
                                               None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        hor_con = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver
