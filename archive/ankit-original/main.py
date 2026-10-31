
import cv2
import mediapipe as mp
import pyautogui
import time

from pathlib import Path
from collections import deque
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# =====================================================
# 1. CONFIGURATION
# =====================================================
click_latched = False
PINCH_THRESHOLD = 0.30

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "gesture_recognizer.task"
)

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "Model not found! Put gesture_recognizer.task inside models."
    )

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Cursor smoothing
SMOOTHING = 0.35
previous_x, previous_y = 0, 0

# Scroll configuration
SCROLL_THRESHOLD = 0.018
last_scroll_y = None
last_scroll_time = 0
SCROLL_COOLDOWN = 0.08

# Gesture stabilization
gesture_history = deque(maxlen=5)

# Volume control state
audio_volume = None


# =====================================================
# 2. WINDOWS AUDIO SETUP
# =====================================================

def setup_audio():
    speakers = AudioUtilities.GetSpeakers()

    # Support newer PyCAW versions
    if hasattr(speakers, "EndpointVolume"):
        volume = speakers.EndpointVolume

    else:
        # Compatibility with older PyCAW versions
        interface = speakers.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        volume = cast(
            interface,
            POINTER(IAudioEndpointVolume)
        )

    return volume


def set_mute(mute_status):

    audio_volume.SetMute(mute_status, None)

    if mute_status == 1:
        print("System MUTED")
    else:
        print("System UNMUTED")


def volume_up():

    current_volume = audio_volume.GetMasterVolumeLevelScalar()

    new_volume = min(1.0, current_volume + 0.05)

    audio_volume.SetMasterVolumeLevelScalar(new_volume, None)

    print(f"Volume increased: {int(new_volume * 100)}%")


def volume_down():

    current_volume = audio_volume.GetMasterVolumeLevelScalar()

    new_volume = max(0.0, current_volume - 0.05)

    audio_volume.SetMasterVolumeLevelScalar(new_volume, None)

    print(f"Volume decreased: {int(new_volume * 100)}%")

# =====================================================
# 3. MEDIAPIPE SETUP
# =====================================================

BaseOptions = mp.tasks.BaseOptions

GestureRecognizer = mp.tasks.vision.GestureRecognizer

GestureRecognizerOptions = (
    mp.tasks.vision.GestureRecognizerOptions
)

RunningMode = mp.tasks.vision.RunningMode


options = GestureRecognizerOptions(
    base_options=BaseOptions(
        model_asset_path=str(MODEL_PATH)
    ),

    running_mode=RunningMode.VIDEO,

    num_hands=1,

    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)


# =====================================================
# 4. GESTURE STABILIZATION
# =====================================================

def get_stable_gesture(history):

    if not history:
        return "None"

    most_common = max(
        set(history),
        key=history.count
    )

    if history.count(most_common) >= 4:
        return most_common

    return "None"


# =====================================================
# 5. MOUSE POINTER CONTROL
# =====================================================

def move_mouse(index_finger):

    global previous_x, previous_y

    # Index fingertip coordinates
    x = index_finger.x
    y = index_finger.y

    # Map camera coordinates to screen coordinates
    target_x = int(x * SCREEN_WIDTH)
    target_y = int(y * SCREEN_HEIGHT)

    # Smooth cursor movement
    smooth_x = (
        previous_x
        + (target_x - previous_x) * SMOOTHING
    )

    smooth_y = (
        previous_y
        + (target_y - previous_y) * SMOOTHING
    )

    previous_x = smooth_x
    previous_y = smooth_y

    # Keep cursor within screen boundaries
    smooth_x = max(
        0,
        min(SCREEN_WIDTH - 1, int(smooth_x))
    )

    smooth_y = max(
        0,
        min(SCREEN_HEIGHT - 1, int(smooth_y))
    )

    pyautogui.moveTo(
        smooth_x,
        smooth_y,
        duration=0
    )


def detect_pinch(hand, frame_width, frame_height):

    # Landmark 4 = Thumb tip
    # Landmark 8 = Index finger tip

    thumb = hand[4]
    index = hand[8]

    # Convert normalized coordinates into pixels
    thumb_x = thumb.x * frame_width
    thumb_y = thumb.y * frame_height

    index_x = index.x * frame_width
    index_y = index.y * frame_height

    # Calculate distance between fingertips
    distance = (
        (thumb_x - index_x) ** 2
        + (thumb_y - index_y) ** 2
    ) ** 0.5

    # Normalize using palm size
    wrist = hand[0]
    middle_base = hand[9]

    palm_size = (
        ((wrist.x - middle_base.x) * frame_width) ** 2
        + ((wrist.y - middle_base.y) * frame_height) ** 2
    ) ** 0.5

    if palm_size == 0:
        return False

    ratio = distance / palm_size

    return ratio < PINCH_THRESHOLD



# =====================================================
# 6. SCROLL CONTROL
# =====================================================



def control_scroll(index_finger, frame_width, frame_height):

    global last_scroll_y, last_scroll_time

    # Get index fingertip position
    x = int(index_finger.x * SCREEN_WIDTH)
    y = int(index_finger.y * SCREEN_HEIGHT)

    # Keep cursor within screen
    x = max(0, min(SCREEN_WIDTH - 1, x))
    y = max(0, min(SCREEN_HEIGHT - 1, y))

    # Move cursor to the hand position
    pyautogui.moveTo(x, y, duration=0)

    current_y = index_finger.y

    if last_scroll_y is None:
        last_scroll_y = current_y
        return

    # Calculate vertical movement
    difference = last_scroll_y - current_y

    current_time = time.time()

    if (
        abs(difference) > 0.002
        and current_time - last_scroll_time >= SCROLL_COOLDOWN
    ):

        # Calculate scrolling intensity
        scroll_amount = int(difference * 500)

        # Ensure at least one scroll step
        if difference > 0:
            scroll_amount = max(1, scroll_amount)
        else:
            scroll_amount = min(-1, scroll_amount)

        # Limit scroll speed
        scroll_amount = max(-10, min(10, scroll_amount))

        pyautogui.scroll(scroll_amount)

        if scroll_amount > 0:
            print("SCROLL UP:", scroll_amount)
        else:
            print("SCROLL DOWN:", scroll_amount)

        last_scroll_time = current_time

    last_scroll_y = current_y



# =====================================================
# 7. MAIN PROGRAM
# =====================================================

def main():

    global audio_volume
    global last_scroll_y

    audio_volume = setup_audio()

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Webcam could not be opened.")
        return

    armed = False

    previous_gesture = "None"

    print("\n===================================")
    print(" SMART HAND GESTURE CONTROL")
    print("===================================")
    print("E = Enable / Disable controls")
    print("Q = Quit")
    print("Controls start DISABLED.")
    print("===================================\n")

    try:

        with GestureRecognizer.create_from_options(options) as recognizer:

            while True:

                success, frame = camera.read()

                if not success:
                    print("Camera frame error.")
                    break

                # Mirror camera
                frame = cv2.flip(frame, 1)

                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame
                )

                timestamp_ms = time.monotonic_ns() // 1_000_000

                result = recognizer.recognize_for_video(
                    mp_image,
                    timestamp_ms
                )

                detected_gesture = "None"
                confidence = 0.0

                index_finger = None

                # Read gesture recognition result
                if result.gestures:

                    gesture = result.gestures[0][0]

                    detected_gesture = gesture.category_name
                    confidence = gesture.score

                    if confidence < 0.65:
                        detected_gesture = "None"

                # Get index fingertip landmark
                if result.hand_landmarks:

                    hand = result.hand_landmarks[0]

                    # Landmark 8 = Index fingertip
                    index_finger = hand[8]

                    height, width, _ = frame.shape

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

                        # =====================================
                        # MOUSE CLICK DETECTION
                        # =====================================

                        if armed and result.hand_landmarks:

                            hand = result.hand_landmarks[0]

                            frame_height, frame_width, _ = frame.shape

                            pinch_detected = detect_pinch(
                                hand,
                                frame_width,
                                frame_height
                            )

                            if pinch_detected and not click_latched:

                                pyautogui.click()

                                click_latched = True

                                print("MOUSE CLICK")

                            elif not pinch_detected:

                                click_latched = False

                        else:
                            click_latched = False

                # Stabilize gesture
                gesture_history.append(detected_gesture)

                stable_gesture = get_stable_gesture(
                    gesture_history
                )

                # =====================================
                # COMPUTER CONTROL
                # =====================================

                if armed:

                    if (
                        stable_gesture == "Pointing_Up"
                        and index_finger is not None
                    ):

                        # Move cursor using index finger
                        move_mouse(index_finger)

                        last_scroll_y = None

                    elif (
                        stable_gesture == "Victory"
                        and index_finger is not None
                    ):

                        # Scroll using Victory sign
                        control_scroll(
                            index_finger,
                            frame.shape[1],
                            frame.shape[0]
                        )

                    else:

                        last_scroll_y = None

                    # Execute volume action only once
                    # when a new stable gesture appears

                    if stable_gesture != previous_gesture:

                        if stable_gesture == "Open_Palm":

                            set_mute(0)

                        elif stable_gesture == "Closed_Fist":

                            set_mute(1)

                        elif stable_gesture == "Thumb_Up":

                            volume_up()

                        elif stable_gesture == "Thumb_Down":

                            volume_down()


                else:

                    last_scroll_y = None

                previous_gesture = stable_gesture

                # =====================================
                # DISPLAY INFORMATION
                # =====================================

                status = (
                    "ENABLED" if armed else "DISABLED"
                )

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
                    "E: Toggle Controls | Q: Quit",
                    (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.imshow(
                    "Smart Hand Gesture Control",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                if key == ord("e"):

                    armed = not armed

                    gesture_history.clear()
                    previous_gesture = "None"
                    last_scroll_y = None

                    print(
                        "Controls:",
                        "ENABLED" if armed else "DISABLED"
                    )

                elif key == ord("q"):
                    break

    finally:

        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
