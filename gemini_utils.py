import os
import base64
import io
from PIL import Image
import time
import google.generativeai as genai
# Removed unused imports: datetime, json (not needed for this refactor)
from speech import speak
import cv2

GEMINI_SCENE_PROMPT = """
You are the vision system of a robot. Describe the scene in front of you.
Say exactly: I see the following elements: [list up to 5 distinct objects].
The closest object appears to be [closest object]. The furthest object appears to be [furthest object].
Example: I see the following elements: a red ball, a blue box, a yellow chair. The closest object appears to be a red ball. The furthest object appears to be a yellow chair.
"""

GEMINI_NAVIGATION_PROMPT_TEMPLATE = """
You are the navigation AI for a robot that is 25cm wide. Your task is to guide it to the GOAL OBJECT.
Analyze the current view and provide the following information, each on a new line:
1. GOAL VISIBLE: [Yes/No]
2. GOAL DIRECTION: [Not Visible/Center/Slightly Left/Slightly Right/Far Left/Far Right]
3. GOAL PROXIMITY: [Not Visible/Reachable/Very Close/Near/Medium/Far]
4. PATH STATUS: [Clear/Minor Obstacle/Major Obstacle/Blocked]
5. OBSTACLE INFO: [Describe briefly if Minor or Major Obstacle, otherwise "None"]

Prioritize reaching the GOAL OBJECT safely. Be very concise and follow the format precisely.
Only consider obstacles directly in the robot's 25cm path.
GOAL OBJECT: {goal}
"""

def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Try to load from a .env file if it exists, for convenience
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
        except ImportError:
            pass  # dotenv not installed, that's fine

        if not api_key:  # Still not found
            raise ValueError("GEMINI_API_KEY environment variable not set and not found in .env file.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-1.5-flash")

def encode_frame_to_base64(frame_bgr) -> str:
    # Ensure robust conversion, similar to original code
    try:
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    except cv2.error as e:
        rgb_frame = frame_bgr
    pil_image = Image.fromarray(rgb_frame)
    buffer = io.BytesIO()
    pil_image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def ask_gemini(model, b64_img: str, prompt: str) -> str:
    image_part = {"mime_type": "image/jpeg", "data": b64_img}
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                contents=[prompt, image_part],
                generation_config={"temperature": 0.2, "max_output_tokens": 200},
                stream=False
            )
            response.resolve()
            return response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini API (attempt {attempt + 1}/{max_retries}): {e}")
            if "API key not valid" in str(e) or "permission" in str(e).lower():
                speak("My connection to the vision system failed due to an authentication error. Please check the API key.")
                raise
            if attempt < max_retries - 1:
                speak(f"I'll retry analyzing the scene, attempt {attempt + 2}.")
                time.sleep(2 ** attempt)
            else:
                speak("I'm having trouble analyzing the scene after multiple retries.")
                return ""

def parse_navigation_advice(advice_text: str) -> dict:
    parsed = {
        "goal_visible": None,  # Important to distinguish None from False initially
        "goal_direction": "Not Visible",
        "goal_proximity": "Not Visible",
        "path_status": "Blocked",  # Default to cautious
        "obstacle_info": "None"
    }
    if not advice_text: # Added check for empty advice_text
        speak("I had trouble understanding the scene analysis.")
        return parsed

    lines = advice_text.split('\n')
    for line in lines:
        line = line.strip()
        if line.lower().startswith("1. goal visible:") or line.lower().startswith("goal visible:"):
            value_str = line.split(":", 1)[1].strip().lower()
            parsed["goal_visible"] = "yes" in value_str
        elif line.lower().startswith("2. goal direction:") or line.lower().startswith("goal direction:"):
            parsed["goal_direction"] = line.split(":", 1)[1].strip().lower()
        elif line.lower().startswith("3. goal proximity:") or line.lower().startswith("goal proximity:"):
            parsed["goal_proximity"] = line.split(":", 1)[1].strip().lower()
        elif line.lower().startswith("4. path status:") or line.lower().startswith("path status:"):
            parsed["path_status"] = line.split(":", 1)[1].strip().lower()
        elif line.lower().startswith("5. obstacle info:") or line.lower().startswith("obstacle info:"):
            parsed["obstacle_info"] = line.split(":", 1)[1].strip().lower()

    if parsed["goal_visible"] is None:  # If visibility wasn't explicitly parsed
        speak("My analysis about goal visibility was incomplete. Assuming not visible.")
        print(f"Problematic Gemini response for visibility: \n{advice_text}") # Added print for debugging
        parsed["goal_visible"] = False

    return parsed