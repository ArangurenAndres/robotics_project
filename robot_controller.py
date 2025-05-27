try:
    import picar_4wd as fc
    ON_ROBOT = True
    print("[INFO] robot_controller loaded successfully.")
except ImportError:
    print("WARNING: picar_4wd not found. Using mock motor functions.")
    ON_ROBOT = False
import time

POWER = 70
DEFAULT_TURN_DURATION = 0.45
DEFAULT_MOVE_DURATION = 0.5

if ON_ROBOT: # Actual robot functions
    def forward(duration=DEFAULT_MOVE_DURATION):
        print(f"\U0001F697 Moving forward for {duration:.2f}s")
        fc.forward(POWER)
        time.sleep(duration)
        fc.stop()

    def backward(duration=DEFAULT_MOVE_DURATION):
        print(f"\u21A9\uFE0F Moving backward for {duration:.2f}s")
        fc.backward(POWER)
        time.sleep(duration)
        fc.stop()

    def left(duration=DEFAULT_TURN_DURATION):
        print(f"\u21AA\uFE0F Turning left for {duration:.2f}s")
        fc.turn_left(POWER)
        time.sleep(duration)
        fc.stop()

    def right(duration=DEFAULT_TURN_DURATION):
        print(f"\u21A9\uFE0F Turning right for {duration:.2f}s") # Changed emoji to match original
        fc.turn_right(POWER)
        time.sleep(duration)
        fc.stop()

    def stop():
        print("\u26D4 Stopping")
        fc.stop()

    def execute_move(move_function, duration: float):
        if not callable(move_function):
            print(f"\u26A0\uFE0F Invalid move function: {move_function}")
            return
        try:
            print(f"\U0001F680 Executing move: {move_function.__name__} for {duration:.2f}s")
            move_function(duration)
        except Exception as e:
            print(f"\u274C Error while executing {move_function.__name__}: {e}")

else: # Mock functions when not ON_ROBOT
    def forward(duration=DEFAULT_MOVE_DURATION):
        print(f"[MOCK MOTOR] Move forward for {duration}s")

    def backward(duration=DEFAULT_MOVE_DURATION):
        print(f"[MOCK MOTOR] Move backward for {duration}s")

    def left(duration=DEFAULT_TURN_DURATION):
        print(f"[MOCK MOTOR] Turn left for {duration}s")

    def right(duration=DEFAULT_TURN_DURATION):
        print(f"[MOCK MOTOR] Turn right for {duration}s")

    def stop():
        print("[MOCK MOTOR] Stop motors")

    def execute_move(move_function, duration: float):
        print(f"[MOCK MOTOR] Executing: {move_function.__name__}({duration})")
        # time.sleep(duration) # Be careful with this in mock if main loop also sleeps
