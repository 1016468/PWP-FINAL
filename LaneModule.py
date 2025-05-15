import cv2
import numpy as np
import utils


def getLaneCurve(img, display=2):
    curveList = []
    avgVal = 8  # Reduced from 10 for faster response to turns
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
    # Amplify the curve value to detect sharper turns
    amplification = 1.3  # Amplify curve value by 30%
    curve = (curve / 100) * amplification
    
    # Keep within normal bounds
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
