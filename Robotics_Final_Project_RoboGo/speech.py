from gtts import gTTS
import subprocess

def speak(text: str):
    # Print the text that the robot will "speak".
    print(f"[Robot says]: {text}")
    try:
        # Use Google Text-to-Speech to generate audio.
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        # Play the generated speech with mpg123 (silent output, 10s timeout for safety).
        subprocess.run(["mpg123", "-q", "output.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    except FileNotFoundError: 
        # If mpg123 is missing, notify that playback won't work.
        print("WARNING: mpg123 not found. Cannot play speech.")
    except Exception as e:
        # Handle other unexpected errors in speech synthesis or playback.
        print(f"Speech synthesis/playback error: {e}") 