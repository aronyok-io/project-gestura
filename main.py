
import cv2
import mediapipe as mp
import pyautogui
import time
from collections import deque
from pathlib import Path

# ---------------- CONFIGURATION ----------------

MODEL_PATH = Path("models/gesture_recognizer.task")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "Model not found! Put gesture_recognizer.task inside the models folder."
    )

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

# Computer actions assigned to gestures
GESTURE_ACTIONS = {
    "Pointing_Up": "right",       # Next slide
    "Victory": "left",            # Previous slide
    "Open_Palm": "space",         # Pause / play
    "Closed_Fist": "volumemute",  # Mute
    "Thumb_Up": "volumeup",       # Volume up
    "Thumb_Down": "volumedown"    # Volume down
}

# ---------------- MEDIAPIPE SETUP ----------------

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
RunningMode = mp.tasks.vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
    running_mode=RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)

# ---------------- GESTURE FILTER ----------------

gesture_history = deque(maxlen=5)

def get_stable_gesture(history):
    if not history:
        return "None"

    most_common = max(set(history), key=history.count)

    if history.count(most_common) >= 4:
        return most_common

    return "None"


# ---------------- MAIN PROGRAM ----------------

def main():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Webcam could not be opened.")
        return

    armed = False
    previous_gesture = "None"
    last_action_time = 0
    cooldown = 1.0

    print("\nSMART HAND GESTURE CONTROL")
    print("--------------------------------")
    print("E = Enable / Disable computer control")
    print("Q = Quit")
    print("Keep control DISABLED until you are ready.")
    print("--------------------------------\n")

    try:
        with GestureRecognizer.create_from_options(options) as recognizer:

            while True:

                success, frame = camera.read()

                if not success:
                    print("Could not read webcam frame.")
                    break

                # Mirror the camera view
                frame = cv2.flip(frame, 1)

                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert frame to MediaPipe image
                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame
                )

                # Recognize hand gestures
                timestamp_ms = time.monotonic_ns() // 1_000_000

                result = recognizer.recognize_for_video(
                    mp_image,
                    timestamp_ms
                )

                detected_gesture = "None"
                confidence = 0.0

                # Read gesture result
                if result.gestures:
                    gesture = result.gestures[0][0]
                    detected_gesture = gesture.category_name
                    confidence = gesture.score

                    if confidence < 0.65:
                        detected_gesture = "None"

                # Draw detected hand landmarks
                if result.hand_landmarks:
                    height, width, _ = frame.shape

                    for hand in result.hand_landmarks:
                        for landmark in hand:
                            x = int(landmark.x * width)
                            y = int(landmark.y * height)

                            cv2.circle(
                                frame,
                                (x, y),
                                5,
                                (0, 255, 0),
                                -1
                            )

                # Stabilize gesture
                gesture_history.append(detected_gesture)
                stable_gesture = get_stable_gesture(
                    list(gesture_history)
                )

                # Execute action only when a new stable gesture appears
                current_time = time.time()

                if (
                    armed
                    and stable_gesture != "None"
                    and stable_gesture != previous_gesture
                    and stable_gesture in GESTURE_ACTIONS
                    and current_time - last_action_time >= cooldown
                ):
                    action = GESTURE_ACTIONS[stable_gesture]

                    try:
                        pyautogui.press(action)
                        print(f"{stable_gesture} -> {action}")
                        last_action_time = current_time

                    except Exception as error:
                        print("Action error:", error)

                previous_gesture = stable_gesture

                # Display information
                status = "ENABLED" if armed else "DISABLED"

                cv2.putText(
                    frame,
                    f"Control: {status}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0) if armed else (0, 0, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Gesture: {detected_gesture}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Confidence: {confidence:.2f}",
                    (20, 115),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "E: Toggle Control | Q: Quit",
                    (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.imshow("Smart Hand Gesture Control", frame)

                # Keyboard controls
                key = cv2.waitKey(1) & 0xFF

                if key == ord("e"):
                    armed = not armed
                    gesture_history.clear()
                    previous_gesture = "None"
                    print("Computer control:", "ENABLED" if armed else "DISABLED")

                elif key == ord("q"):
                    break

    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()