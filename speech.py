from gtts import gTTS
import subprocess

def speak(text: str):
    print(f"[Robot says]: {text}")
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        # Use a timeout for mpg123 to prevent it from hanging
        subprocess.run(["mpg123", "-q", "output.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    except FileNotFoundError: # Added specific error handling
        print("WARNING: mpg123 not found. Cannot play speech.")
    except Exception as e:
        print(f"Speech synthesis/playback error: {e}") # Changed print statement