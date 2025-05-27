import time
import numpy as np
import cv2

# A single mock camera class that simulate a feed for testing purposes.
class MockCamera:
    def __init__(self, width, height, name="MockCamera"):
        self.width = width
        self.height = height
        self.name = name
        self.is_running = False
        # Inform thatthe mock camera has been initialized with the given resolutiom.
        print(f"[MOCK CAM] {self.name} initialized ({width}x{height}).") 

    # Start the mock simulation.
    def start(self):
        self.is_running = True
        print(f"[MOCK CAM] {self.name} started.") 

    def capture_array(self, name="main"):
        # If the camera has not started, return blank picture.
        if not self.is_running:
            print(f"[MOCK CAM] {self.name} capture_array called but camera not started.") 
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Create blank picture.
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Add a line that shifts positions based on time to simulation motion.
        tick = int(time.time() * 10) % self.width
        cv2.line(frame, (tick, 0), (self.width - tick, self.height - 1), (0, 255, 0), 2)
        cv2.putText(frame, f"{time.strftime('%H:%M:%S')}", (10, self.height - 10), # Added timestamp.
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        time.sleep(0.05) # Simulate capture time.
        return frame

    # Stop the mock camera.
    def stop(self):
        self.is_running = False
        print(f"[MOCK CAM] {self.name} stopped.")

    def __enter__(self): 
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): # Added context manager methods.
        self.stop()

# Import the PiCamera2 library.
try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    # If PiCamera unavailable, fallback to using mock camera.
    PICAMERA_AVAILABLE = False
    print("WARNING: Picamera2 library not found. Camera functionality will be mocked.") 
except Exception as e: # Catch other potential import errors.
    PICAMERA_AVAILABLE = False
    print(f"WARNING: Error importing Picamera2: {e}. Camera functionality will be mocked.") 

# If camera available, confugure. If not, use mock camera.
def setup_camera(width=320, height=240):
    if PICAMERA_AVAILABLE:
        try:
            # Create a video configuration.
            cam = Picamera2()
            config = cam.create_video_configuration(main={"size": (width, height), "format": "RGB888"})
            cam.configure(config)
            print(f"[INFO] Picamera2 setup complete ({width}x{height}, format RGB888).") 
            return cam
        except Exception as e: # Catch camera specific initialization errors.
            print(f"Failed to initialize Picamera2: {e}. Using mock camera.") 
            return MockCamera(width, height, name="Picamera2_Fallback_Mock")
    else:
        print("[INFO] Using MockCamera as Picamera2 is not available.") 
        return MockCamera(width, height)