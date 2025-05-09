import cv2
import time

# Cache for the camera object
_camera_cache = None
_last_camera_index = None

def getImg(display=False, size=[480, 240]):
    """
    Get an image from the webcam - headless version optimized for robot operation
    Returns the image or None if no camera is available
    """
    global _camera_cache, _last_camera_index
    
    # Try to use cached camera first
    if _camera_cache is not None:
        success, img = _camera_cache.read()
        if success:
            return img
        else:
            # Camera read failed, close and try to reinitialize
            _camera_cache.release()
            _camera_cache = None
            print("Camera connection lost, attempting to reconnect...")
    
    # Try different camera indices if cache failed or doesn't exist
    for camera_index in [0, 1, 2]:
        try:
            cap = cv2.VideoCapture(camera_index)
            
            if cap.isOpened():
                # Configure camera properties
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
                
                # Wait a moment for camera to initialize
                time.sleep(0.1)
                
                # Try to read a frame
                success, img = cap.read()
                
                if success:
                    print(f"Connected to camera {camera_index}")
                    _camera_cache = cap
                    _last_camera_index = camera_index
                    return img
                else:
                    cap.release()
        except Exception as e:
            print(f"Error with camera {camera_index}: {e}")
            if 'cap' in locals():
                cap.release()
    
    # If we get here, no camera worked
    print("No working camera found")
    return None

def releaseCamera():
    """Explicitly release the camera resource"""
    global _camera_cache
    if _camera_cache is not None:
        _camera_cache.release()
        _camera_cache = None

if __name__ == '__main__':
    # This section only runs when the module is executed directly
    # It won't run when imported by the main script
    print("Testing camera in headless mode...")
    img = getImg(False)
    if img is not None:
        h, w, _ = img.shape
        print(f"Camera working. Image size: {w}x{h}")
    else:
        print("No camera detected")
    releaseCamera()
