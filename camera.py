import time
import numpy as np
import cv2

class MockCamera:
    def __init__(self, width, height, name="MockCamera"):
        self.width = width
        self.height = height
        self.name = name
        self.is_running = False
        print(f"[MOCK CAM] {self.name} initialized ({width}x{height}).") # Added print

    def start(self):
        self.is_running = True
        print(f"[MOCK CAM] {self.name} started.") # Added print

    def capture_array(self, name="main"):
        if not self.is_running:
            print(f"[MOCK CAM] {self.name} capture_array called but camera not started.") # Added print
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)

        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        tick = int(time.time() * 10) % self.width
        cv2.line(frame, (tick, 0), (self.width - tick, self.height - 1), (0, 255, 0), 2)
        cv2.putText(frame, f"{time.strftime('%H:%M:%S')}", (10, self.height - 10), # Added timestamp
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        time.sleep(0.05) # Simulate capture time
        return frame

    def stop(self):
        self.is_running = False
        print(f"[MOCK CAM] {self.name} stopped.") # Added print

    def __enter__(self): # s
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): # Added context manager methods
        self.stop()


try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    print("WARNING: Picamera2 library not found. Camera functionality will be mocked.") # Added print
except Exception as e: # Catch other potential import errors
    PICAMERA_AVAILABLE = False
    print(f"WARNING: Error importing Picamera2: {e}. Camera functionality will be mocked.") # Added print


def setup_camera(width=320, height=240):
    if PICAMERA_AVAILABLE:
        try:
            cam = Picamera2()
            config = cam.create_video_configuration(main={"size": (width, height), "format": "RGB888"})
            cam.configure(config)
            print(f"[INFO] Picamera2 setup complete ({width}x{height}, format RGB888).") # Added print
            return cam
        except Exception as e: # Catch camera specific initialization errors
            print(f"Failed to initialize Picamera2: {e}. Using mock camera.") # Added print
            return MockCamera(width, height, name="Picamera2_Fallback_Mock")
    else:
        print("[INFO] Using MockCamera as Picamera2 is not available.") # Added print
        return MockCamera(width, height)