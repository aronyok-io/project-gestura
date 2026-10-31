# Architecture

`main.py` opens the Tkinter GUI. `core/runner.py` owns a background worker, camera, tracker and Windows controller. Configuration is loaded by core/settings.py from config/settings.json. Queues carry commands, status and preview frames; Tk widgets are updated only on the GUI thread.

`vision/camera.py` captures mirrored frames. `vision/hand_tracker.py` runs MediaPipe and draws landmarks. `vision/gesture_recognizer.py` translates model labels and calculates palm-normalized pinch distance.

Sample contract: `{"gesture": "POINT", "position": (0.5, 0.5), "detected": True, "pinch_ratio": 0.8}`. Coordinates refer to the mirrored frame, normalized to 0–1. No-hand samples use `NONE`, `None` position, and `False` detection.

`control/action_mapper.py` handles confirmation, pinch latching and scroll policy. `control/windows_controller.py` executes actions. `control/mock_controller.py` records them without desktop access. `core/state_manager.py` maintains enable/mode state.

No webcam recording or uploads. Audio is initialized only when used; audio failure leaves mouse mode available.

Windows setup and launch scripts live in scripts/. main.py --check validates imports and the model bundle without opening the camera. Tracking and startup tracebacks are written to logs/gestura.log. The Windows CI workflow checks installation and regression tests; physical camera recognition and desktop input still require the acceptance checklist.
