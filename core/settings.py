import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_settings():
    with (ROOT / "config" / "settings.json").open(encoding="utf-8") as stream:
        settings = json.load(stream)
    if type(settings["camera_index"]) is not int or settings["camera_index"] < 0:
        raise ValueError("camera_index must be a nonnegative integer")
    if not 0 < settings["pinch_press"] < settings["pinch_release"] < 2:
        raise ValueError("Pinch thresholds must satisfy 0 < press < release < 2")
    if not 0 < settings["smoothing"] <= 1:
        raise ValueError("smoothing must be between 0 and 1")
    for key in ("gesture_delay", "pinch_delay"):
        if not 0 <= settings[key] <= 2:
            raise ValueError(f"{key} must be between 0 and 2 seconds")
    return settings
