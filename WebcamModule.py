
import cv2

def getImg(display=False, size=[480, 240]):
    try:
        # Try different camera indices if 0 doesn't work
        for camera_index in [0, 1, 2]:
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
                success, img = cap.read()
                if success:
                    return img
                cap.release()
    except Exception as e:
        print(f"Camera error: {e}")
    return None

if __name__ == '__main__':
    while True:
        img = getImg(True)
        if img is not None:
            cv2.imshow('Image', img)
        else:
            print("No camera found or error reading image")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
