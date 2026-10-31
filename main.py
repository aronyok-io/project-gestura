"""Windows application entry point. --check diagnoses installation problems."""
import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description="Gestura hand gesture control for Windows")
    parser.add_argument("--check", action="store_true", help="Check installation without opening the webcam")
    parser.add_argument("--mock", action="store_true", help="Developer simulation; no real desktop actions")
    args = parser.parse_args()
    if args.check:
        from core.diagnostics import check_environment
        return check_environment()
    if sys.platform != "win32" and not args.mock:
        print("Gestura desktop control runs on Windows. Use Ankit's Windows machine.")
        return 1
    log_directory = Path(__file__).resolve().parent / "logs"
    try:
        log_directory.mkdir(exist_ok=True)
        logging.basicConfig(level=logging.INFO, handlers=[RotatingFileHandler(
            log_directory / "gestura.log", maxBytes=1_000_000, backupCount=2, encoding="utf-8")])
        from interface.app import App
        App(mock=args.mock).mainloop()
    except Exception:
        logging.exception("Application startup failed")
        print("Gestura could not start. Details:", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
