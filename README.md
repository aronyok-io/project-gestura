# GESTURA

A Windows desktop application for local webcam hand tracking, mouse control and media control.

## Run on Windows

1. Install **64-bit Python 3.12**, including Tcl/Tk and the Python launcher.
2. Download/clone the repository and run `scripts\setup_windows.bat` once.
3. Run `scripts\run_windows.bat`.
4. Select Mouse or Media mode, start tracking, then enable controls.

The supplied model is included in `models/gesture_recognizer.task`. No model download is required.
Stop disables control and releases the camera. Moving the physical pointer into a PyAutoGUI fail-safe corner stops tracking. Esc stops while the app window has focus.

| Mode | Gesture | Action |
|---|---|---|
| Mouse | Pointing index | Move cursor |
| Mouse | Thumb/index pinch | Single left click; release before another click |
| Mouse | Victory sign | Scroll vertically |
| Mouse | Fist / open palm | Pause / resume cursor control |
| Media | Thumb up/down | Volume +/-5% per gesture |
| Media | Fist/open palm | Mute/unmute |

## Repository

- `main.py` — startup, diagnostics and logging
- `vision/` — camera capture, MediaPipe tracking and gesture classification
- `control/` — gesture/action mapping and Windows desktop backend
- `core/` — state, stabilization, settings and processing worker
- `interface/` — application window and reusable components
- `config/settings.json` — camera index, smoothing and gesture thresholds
- `models/` — supplied pretrained model
- `scripts/` — Windows installation and launch commands
- `tests/` — automated logic and backend regression checks
- `docs/` — architecture, installation, gesture reference and Windows test checklist
- `.github/workflows/tests.yml` — Windows installation/import and regression checks

## Execution problems

Run `.venv\Scripts\python.exe main.py --check` from a terminal. It checks dependencies, configuration and model integrity without opening the camera or controlling the desktop.

Runtime tracebacks are recorded in `logs/gestura.log`. Copy the exact terminal error or log traceback when reporting a failure. Never commit diagnostic logs.

[Installation and troubleshooting](docs/installation.md) · [Architecture](docs/architecture.md) · [Windows acceptance checklist](docs/windows-test-checklist.md)

Automated checks: `python -m unittest discover -v`. They use substitutes for hardware, so passing tests does not establish webcam accuracy or successful real Windows execution. Ankit must complete the hardware checklist. `--mock` is an optional developer simulator, not the demonstration or Windows acceptance test.

## Original upload backup

Ankit’s unchanged original source and dependency list are preserved in [`archive/ankit-original/`](archive/ankit-original/), with the source commit recorded in `ORIGIN.md`.
