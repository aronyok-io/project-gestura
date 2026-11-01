"""Startup checks that do not open the webcam or issue desktop actions."""
import importlib
import importlib.metadata
import sys
import zipfile
from core.settings import ROOT, load_settings


def check_environment():
    failures = []
    print(f"Python: {sys.version.split()[0]} ({sys.platform})")
    if sys.platform != "win32":
        failures.append("Real Gestura execution requires Windows.")
    for module, package in (("tkinter", None), ("PIL.ImageTk", "pillow"),
                            ("cv2", "opencv-contrib-python"), ("mediapipe", "mediapipe"),
                            ("pyautogui", "pyautogui"), ("comtypes", "comtypes"),
                            ("pycaw.pycaw", "pycaw")):
        try:
            loaded = importlib.import_module(module)
            if module == "mediapipe":
                _ = loaded.tasks.vision.GestureRecognizer
            version = importlib.metadata.version(package) if package else "bundled"
            print(f"OK: {module} ({version})")
        except Exception as error:
            failures.append(f"{module}: {error}")
    try:
        load_settings()
        model = ROOT / "models" / "gesture_recognizer.task"
        with zipfile.ZipFile(model) as bundle:
            if bundle.testzip() or not {"hand_landmarker.task", "hand_gesture_recognizer.task"} <= set(bundle.namelist()):
                raise ValueError("Model bundle is invalid")
        print("OK: configuration and model bundle")
    except Exception as error:
        failures.append(f"Configuration/model: {error}")
    for failure in failures:
        print("ERROR:", failure)
    return 1 if failures else 0
