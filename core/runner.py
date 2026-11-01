"""Worker owns camera, recognition, COM and desktop backend; GUI communicates via queues."""
import queue
import threading
import time
import logging
from core.settings import load_settings
from control.action_mapper import ActionMapper
from core.state_manager import StateManager


class Runner:
    def __init__(self, mock=False):
        self.mock = mock
        self.commands = queue.Queue()
        self.events = queue.Queue(maxsize=100)
        self.frames = queue.Queue(maxsize=1)
        self.stop_event = threading.Event()
        self.thread = None

    def emit(self, kind, value):
        try:
            self.events.put_nowait((kind, value))
        except queue.Full:
            if kind != "sample":
                try:
                    self.events.get_nowait()
                except queue.Empty:
                    pass
                self.events.put_nowait((kind, value))

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        for channel in (self.commands, self.events, self.frames):
            while True:
                try:
                    channel.get_nowait()
                except queue.Empty:
                    break
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def run(self):
        camera = tracker = controller = None
        state = StateManager()
        sample = {"gesture": "NONE", "position": (0.5, 0.5), "detected": False, "pinch_ratio": None}
        try:
            if self.mock:
                from control.mock_controller import MockController
                controller = MockController(lambda text: self.emit("log", text))
            else:
                import sys
                if sys.platform != "win32":
                    raise RuntimeError("Use --mock on Fedora; real desktop control currently supports Windows.")
                from control.windows_controller import WindowsController
                from vision.camera import Camera
                from vision.hand_tracker import HandTracker
                settings = load_settings()
                controller = WindowsController(lambda text: self.emit("log", text), smoothing=settings["smoothing"])
                tracker = HandTracker()
                camera = Camera(settings["camera_index"])
            mapper = ActionMapper(controller)
            self.emit("status", "Tracking — controls disabled")
            while not self.stop_event.is_set():
                while True:
                    try:
                        command, value = self.commands.get_nowait()
                    except queue.Empty:
                        break
                    if command == "enabled":
                        state.enabled = value
                        state.paused = False
                        mapper.reset()
                    elif command == "mode":
                        state.set_mode(value)
                        mapper.reset()
                    elif command == "sample":
                        sample = value
                now = time.monotonic()
                if self.mock:
                    self.stop_event.wait(0.03)
                else:
                    sample, rgb = tracker.process(camera.read(), now)
                    if self.frames.full():
                        try:
                            self.frames.get_nowait()
                        except queue.Empty:
                            pass
                    self.frames.put_nowait(rgb)
                if self.stop_event.is_set():
                    break
                was_paused = state.paused
                mapper.process(sample, state, now)
                if state.paused != was_paused:
                    self.emit("status", "Mouse paused — open palm to resume" if state.paused else "Controls enabled")
                self.emit("sample", sample["gesture"] if sample["detected"] else "No hand")
        except Exception as error:
            logging.exception("Tracking stopped")
            self.emit("error", f"Controls stopped: {error}")
        finally:
            for resource in (camera, tracker, controller):
                if resource:
                    try:
                        resource.close()
                    except Exception as error:
                        self.emit("log", f"Cleanup: {error}")
            self.emit("stopped", None)
