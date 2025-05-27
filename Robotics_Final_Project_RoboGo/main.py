import os
import time
import cv2
import traceback # Import traceback for detailed error logging.

from gemini_utils import configure_gemini, ask_gemini, encode_frame_to_base64, GEMINI_SCENE_PROMPT
from camera import setup_camera
from navigation import pursue_object
from speech import speak
from robot_controller import stop, ON_ROBOT # Import stop and ON_ROBOT.


def main():
    CAMERA_WIDTH = 320
    CAMERA_HEIGHT = 240
    # TFLITE_MODEL_PATH = "Sample_TFLite_model/detect.tflite" # Path to your TFLite model.
    # LABEL_MAP_PATH = "/home/pi/robotics/project/labelmap.txt" # Path to your labelmap.

    # Initialize Gemini AI model; ensure credentials are set.
    try:
        model_gemini = configure_gemini()
    except ValueError as e:
        print(f"FATAL ERROR: {e}")
        speak("There was a critical error setting up my vision system. I cannot proceed.")
        return
    except Exception as e:
        print(f"FATAL ERROR during Gemini configuration: {e}")
        speak("An unexpected error occurred while setting up my vision system.")
        return

    # Using context manager for camera if Picamera2, or if MockCamera implements it.
    # Use 'with' statement for robustness, as defined in camera.py's MockCamera __enter__/__exit__.
    with setup_camera(CAMERA_WIDTH, CAMERA_HEIGHT) as camera_resource: # Use 'with' statement.
        # Manual start for Picamera2, as it might not be in context manager yet if not the actual type.
        # Or if Picamera2 needs a separate start call outside the __enter__ for some reason.
        # The 'with' statement will call .start() for MockCamera.
        # This explicit check makes it identical to the original logic.
        try:
            from picamera2 import Picamera2 # Re-import to check type.
            if isinstance(camera_resource, Picamera2):
                camera_resource.start()
                print("[INFO] Picamera2 started.")
        except ImportError:
            pass # Picamera2 not available, so it's a MockCamera, already started by 'with'.

        try:
            speak("Hello! I'm ready. Let me take a look around.")
            time.sleep(0.5)
            initial_frame_rgb = camera_resource.capture_array(name="main")

            # If an image was captured, send it to Gemini for scene description.
            if initial_frame_rgb is not None and initial_frame_rgb.size > 0:
                b64_initial_img = encode_frame_to_base64(initial_frame_rgb)
                scene_description = ask_gemini(model_gemini, b64_initial_img, GEMINI_SCENE_PROMPT)
                if scene_description:
                    speak(scene_description)
                else:
                    speak("I had trouble describing the initial scene.")
            else:
                speak("I couldn't get an initial image from the camera.")
            
            # Prompt user for the goal object to pursue.
            goal_object_input = ""
            while not goal_object_input:
                goal_object_input = input(
                    "\n[USER INPUT] What object should I look for? (e.g., 'red ball') ").strip().lower()
                if not goal_object_input:
                    speak("Please tell me what to look for.")

            # Start the pursuit task with Gemini and camera.
            pursuit_successful = pursue_object(model_gemini, camera_resource, goal_object_input)

            if pursuit_successful:
                speak("I found it! Task complete.")
            else:
                speak("I tried my best but couldn't complete the task this time.")

        except KeyboardInterrupt:
            print("\n[INFO] Program interrupted by user.")
            speak("Okay, stopping now.")
        except Exception as e:
            print(f"[FATAL ERROR] An unexpected error occurred in main loop: {e}")
            speak("Oh dear, something went very wrong.")
            traceback.print_exc() # Print full traceback for debugging
        finally:
            print("[INFO] Program shutting down.")
            # Camera resource is stopped by the 'with' statement's __exit__
            if ON_ROBOT:
                stop() # Ensure motors are stopped
            cv2.destroyAllWindows() # Clean up any OpenCV windows if opened.


if __name__ == "__main__":
    # Check for GEMINI_API_KEY early, before trying to use it.
    if not os.getenv("GEMINI_API_KEY"):
        print("---------------------------------------------------------------------------")
        print("ERROR: The GEMINI_API_KEY environment variable is not set.")
        print("Please set it before running the script. You can do this by:")
        print("1. Exporting it in your terminal: export GEMINI_API_KEY='your_api_key_here'")
        print("2. Creating a '.env' file in the same directory with the line: GEMINI_API_KEY='your_api_key_here'")
        print("   (If using .env, ensure 'python-dotenv' is installed: pip install python-dotenv)")
        print("---------------------------------------------------------------------------")
    else:
        main()