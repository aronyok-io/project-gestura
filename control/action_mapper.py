from core.gesture_stabilizer import GestureStabilizer
from core.settings import load_settings


class ActionMapper:
    """Pure gesture policy. Coordinates passed to controllers are normalized."""
    def __init__(self, controller):
        self.controller = controller
        self.settings = load_settings()
        self.stabilizer = GestureStabilizer(self.settings["gesture_delay"])
        self.reset()

    def reset(self):
        self.stabilizer.reset()
        self.previous = "NONE"
        self.pinched = False
        self.pinch_since = None
        self.scroll_y = None
        self.scroll_time = 0.0
        self.controller.reset()

    def process(self, sample, state, now):
        if not state.enabled or not sample["detected"]:
            self.reset()
            return
        position = sample.get("position")
        ratio = sample.get("pinch_ratio")
        if state.mode == "Mouse" and ratio is not None:
            if ratio < self.settings["pinch_press"]:
                if self.pinch_since is None:
                    self.pinch_since = now
                if not self.pinched and now - self.pinch_since >= self.settings["pinch_delay"]:
                    self.controller.click()
                    self.pinched = True
                # Freeze pointer and reset scroll while pinching.
                self.scroll_y = None
                self.stabilizer.reset()
                return
            if ratio > self.settings["pinch_release"]:
                self.pinched = False
                self.pinch_since = None
            elif self.pinch_since is not None:
                return
        else:
            self.pinched = False
            self.pinch_since = None

        gesture = self.stabilizer.update(sample["gesture"], now)
        if state.mode == "Mouse":
            if gesture == "POINT" and position is not None:
                self.controller.move(*position)
                self.scroll_y = None
            elif gesture == "TWO_FINGERS" and position is not None:
                y = position[1]
                if self.scroll_y is None:
                    self.scroll_y, self.scroll_time = y, now
                elif now - self.scroll_time >= 0.08:
                    difference = self.scroll_y - y
                    if abs(difference) >= 0.018:
                        amount = max(-5, min(5, round(difference * 100)))
                        self.controller.scroll(amount)
                        self.scroll_y, self.scroll_time = y, now
            else:
                self.scroll_y = None
        elif gesture != self.previous:
            action = {"OPEN_PALM": "unmute", "FIST": "mute",
                      "THUMB_UP": "volumeup", "THUMB_DOWN": "volumedown"}.get(gesture)
            if action:
                self.controller.media(action)
        # Do not re-arm media actions on a brief uncertain classification.
        if gesture != "NONE" or (self.stabilizer.candidate == "NONE"
                and self.stabilizer.since is not None
                and now - self.stabilizer.since >= self.stabilizer.delay):
            self.previous = gesture
