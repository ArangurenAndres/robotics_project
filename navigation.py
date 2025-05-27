import random
import time
from speech import speak
from robot_controller import forward, backward, left, right, stop, execute_move, ON_ROBOT # Import ON_ROBOT
from gemini_utils import encode_frame_to_base64, ask_gemini, parse_navigation_advice, GEMINI_NAVIGATION_PROMPT_TEMPLATE

def pursue_object(model, camera, goal_object: str):
    print(f"\n[INFO] Starting pursuit of: {goal_object.upper()}") # Added print
    speak(f"Okay, I will look for the {goal_object}.")

    MAX_STEPS = 40
    REACHED_PROXIMITY = ["reachable", "very close"]
    LOST_GOAL_COUNT_THRESHOLD = 3
    MAX_CORRECTIONS = 2 # Added MAX_CORRECTIONS

    lost_goal_counter = 0
    consecutive_blocked_counter = 0 # Added consecutive_blocked_counter
    correction_count = 0 # Added correction_count

    nav_prompt_formatted = GEMINI_NAVIGATION_PROMPT_TEMPLATE.format(goal=goal_object) # Changed variable name to match original

    for step in range(MAX_STEPS):
        print(f"\n🔄 Step {step + 1}/{MAX_STEPS} | Goal: {goal_object.upper()}") # Added print
        frame_rgb = camera.capture_array(name="main")

        if frame_rgb is None or frame_rgb.size == 0: # Added robust check for empty frame
            speak("I couldn't get an image from the camera for this step.")
            time.sleep(1)
            continue

        b64_img = encode_frame_to_base64(frame_rgb)
        advice_text = ask_gemini(model, b64_img, nav_prompt_formatted) # Used nav_prompt_formatted

        if not advice_text: # Handle empty advice text
            speak("I could not get navigation advice for this view. I will try turning.")
            execute_move(random.choice([left, right]), 0.5)
            time.sleep(0.5)
            continue

        advice = parse_navigation_advice(advice_text) # Correctly parse advice

        print(f"🧠 Gemini Advice:\n" # Added print for advice
              f"  Goal Visible: {advice['goal_visible']}\n"
              f"  Direction: {advice['goal_direction']}\n"
              f"  Proximity: {advice['goal_proximity']}\n"
              f"  Path: {advice['path_status']}\n"
              f"  Obstacle: {advice['obstacle_info']}")

        current_situation_summary = f"Goal is {'' if advice['goal_visible'] else 'not '}visible. "
        if advice['goal_visible']:
            current_situation_summary += f"It's {advice['goal_direction']} and {advice['goal_proximity']}. "
        current_situation_summary += f"Path is {advice['path_status']}"
        if "obstacle" in advice['path_status'].lower() and advice['obstacle_info'] not in ["none", ""]:
            current_situation_summary += f" with {advice['obstacle_info']}."
        speak(current_situation_summary)

        action_taken_this_step = False # Added action_taken_this_step
        can_declare_success_this_step = True # Added can_declare_success_this_step

        proximity_durations = { # Added proximity_durations dictionary
            "very close": 1.2,
            "reachable": 1.6,
            "near": 2.0,
            "medium": 2.2,
            "far": 2.4
        }

        if advice["goal_visible"]:
            lost_goal_counter = 0

            if correction_count < MAX_CORRECTIONS: # Implemented MAX_CORRECTIONS
                if advice["goal_direction"] in ["slightly left", "far left"]:
                    speak(f"Adjusting left toward {goal_object}.")
                    execute_move(left, 0.15 if "slightly" in advice["goal_direction"] else 0.45)
                    correction_count += 1
                elif advice["goal_direction"] in ["slightly right", "far right"]:
                    speak(f"Adjusting right toward {goal_object}.")
                    execute_move(right, 0.15 if "slightly" in advice["goal_direction"] else 0.45)
                    correction_count += 1

            move_duration = proximity_durations.get(advice["goal_proximity"], 0.9) # Get duration from dict

            if advice["path_status"] == "minor obstacle":
                speak("Minor obstacle detected. Adjusting to avoid while staying aligned.")
                execute_move(random.choice([left, right]), 0.15)
                action_taken_this_step = True

            elif advice["path_status"] in ["major obstacle", "blocked"]:
                if advice["goal_proximity"] in REACHED_PROXIMITY:
                    speak("Goal is close. Trying to push forward gently.")
                    execute_move(forward, move_duration)
                else:
                    consecutive_blocked_counter += 1 # Increment counter
                    speak("Path blocked. Reorienting.")
                    execute_move(random.choice([left, right]), 0.6)
                action_taken_this_step = True

            elif advice["path_status"] == "clear":
                speak("Path is clear. Moving toward the object.")
                execute_move(forward, move_duration)
                action_taken_this_step = True

            if can_declare_success_this_step and advice["goal_proximity"] in REACHED_PROXIMITY:
                speak(f"I have reached the {goal_object}! Pursuit successful.")
                stop()
                return True

        else:
            lost_goal_counter += 1
            speak(f"I don't see the {goal_object}.")
            if lost_goal_counter >= LOST_GOAL_COUNT_THRESHOLD:
                speak("Goal lost. Scanning.")
                execute_move(random.choice([left, right]), 0.6)
                lost_goal_counter = 0
            elif advice["path_status"] in ["major obstacle", "blocked"]:
                consecutive_blocked_counter += 1 # Increment counter
                speak("Blocked. Turning.")
                execute_move(random.choice([left, right]), 0.5)
            elif advice["path_status"] == "minor obstacle":
                speak("Minor obstacle ahead. Avoiding.")
                execute_move(random.choice([left, right]), 0.35)
            else:
                speak("Path clear but goal not visible. Exploring.")
                execute_move(random.choice([left, right]), 0.5)
            action_taken_this_step = True

        if not action_taken_this_step and step > 0: # Added this check
            speak("Uncertain. Making a small turn.")
            execute_move(random.choice([left, right]), 0.2)

        print("-" * 30) # Added print for separator
        time.sleep(0.6)

    speak(f"Maximum steps reached. I could not definitively reach the {goal_object}.")
    if ON_ROBOT: # Added ON_ROBOT check
        stop()
    return False