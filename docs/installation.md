# Windows installation and troubleshooting

Use **Python 3.12, 64-bit**, including Tcl/Tk and the Python launcher. Start with a fresh virtual environment rather than reusing a mixed OpenCV/MediaPipe installation.

Run `scripts\setup_windows.bat` once, followed by `scripts\run_windows.bat`. Both scripts select the repository directory automatically and retain installation errors in the terminal.

Equivalent manual commands, from the repository root:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe main.py --check
.venv\Scripts\python.exe main.py
```

The model is included in `models/gesture_recognizer.task`. Configuration and model paths are resolved relative to the source, not the terminal working directory.

| Symptom | Check |
|---|---|
| Missing `pycaw`, `comtypes`, `cv2` or `mediapipe` | Use the same `.venv\Scripts\python.exe` for installation and launch |
| Cannot install MediaPipe | Confirm Python 3.12 and 64-bit Windows; preserve the pip error |
| Webcam unavailable | Close other camera apps, check Windows camera privacy access for desktop apps; change `camera_index` in config/settings.json if needed |
| Missing Tkinter | Modify the Python installation to include Tcl/Tk |
| Broken cv2 import | Create a clean virtual environment; requirements intentionally installs only opencv-contrib-python |
| Controls stop at a screen corner | Move the physical mouse away, restart tracking and explicitly re-enable; this is the fail-safe |
| Audio unavailable | Mouse mode remains usable; inspect the logged message and default Windows audio device |
| Application closes or tracking fails | Run the launch script and copy the traceback from logs/gestura.log |

Versions are constrained to reduce dependency drift, but are not a Windows-tested lockfile. After successful hardware testing, record the exact installed environment using `python -m pip freeze > requirements-windows-tested.txt` and share it with the team.

Run automated regression checks with `python -m unittest discover -v`. Windows hardware acceptance is documented separately.
