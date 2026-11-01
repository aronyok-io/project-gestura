from pathlib import Path
from vision.gesture_recognizer import sample_from_result


class HandTracker:
    def __init__(self):
        import mediapipe as mp
        import cv2
        self.mp, self.cv2 = mp, cv2
        model = Path(__file__).resolve().parents[1] / "models" / "gesture_recognizer.task"
        if not model.is_file():
            raise FileNotFoundError(f"Place gesture_recognizer.task at {model}")
        vision = mp.tasks.vision
        self.recognizer = vision.GestureRecognizer.create_from_options(vision.GestureRecognizerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
            running_mode=vision.RunningMode.VIDEO, num_hands=1,
            min_hand_detection_confidence=0.6, min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6))
        self.last_timestamp = -1

    def process(self, frame, now):
        timestamp = max(self.last_timestamp + 1, int(now * 1000))
        self.last_timestamp = timestamp
        rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        result = self.recognizer.recognize_for_video(
            self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb), timestamp)
        height, width = frame.shape[:2]
        sample = sample_from_result(result, width, height)
        for hand in result.hand_landmarks:
            for landmark in hand:
                self.cv2.circle(frame, (int(landmark.x * width), int(landmark.y * height)), 4, (0, 220, 100), -1)
        return sample, self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)

    def close(self):
        self.recognizer.close()
