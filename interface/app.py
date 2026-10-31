import queue
import tkinter as tk
from tkinter import ttk
from core.runner import Runner
from interface.components import ActivityLog, CameraPreview


class App(tk.Tk):
    def __init__(self, mock=False):
        super().__init__()
        self.title("GESTURA" + (" — Mock mode" if mock else ""))
        self.geometry("860x740")
        self.minsize(720, 650)
        self.runner = Runner(mock)
        self.closing = False
        self.enabled = tk.BooleanVar(value=False)
        self.mode = tk.StringVar(value="Mouse")
        self.status = tk.StringVar(value="Stopped")
        self.gesture = tk.StringVar(value="No hand")
        ttk.Label(self, text="GESTURA", font=("Arial", 26, "bold")).pack(pady=(16, 4))
        ttk.Label(self, text="Local hand tracking · Mouse and media control").pack()
        toolbar = ttk.Frame(self)
        toolbar.pack(pady=12)
        self.start_button = ttk.Button(toolbar, text="Start tracking", command=self.start)
        self.start_button.pack(side="left", padx=5)
        ttk.Button(toolbar, text="STOP / Disable", command=self.stop).pack(side="left", padx=5)
        self.enable_button = ttk.Checkbutton(toolbar, text="Enable controls", variable=self.enabled, command=self.enable, state="disabled")
        self.enable_button.pack(side="left", padx=8)
        selector = ttk.Combobox(toolbar, values=("Mouse", "Media"), textvariable=self.mode, state="readonly", width=10)
        selector.pack(side="left", padx=5)
        selector.bind("<<ComboboxSelected>>", self.change_mode)
        self.preview = CameraPreview(self, "Camera preview" if not mock else "Developer simulation — no desktop actions")
        self.preview.pack(fill="both", expand=True, padx=20, pady=8)
        ttk.Label(self, textvariable=self.status).pack()
        ttk.Label(self, textvariable=self.gesture, font=("Arial", 14)).pack(pady=5)
        ttk.Label(self, text="Mouse: point → move · pinch → click · victory → scroll\nMedia: thumbs → volume · fist → mute · palm → unmute", justify="center").pack()
        ttk.Label(self, text="Esc stops while this window has focus. On Windows, move the physical mouse to a corner for fail-safe.", wraplength=800).pack(pady=5)
        if mock:
            self.mock_controls()
        self.log = ActivityLog(self)
        self.log.pack(fill="x", padx=20, pady=(5, 15))
        self.bind("<Escape>", lambda event: self.stop())
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(30, self.poll)

    def mock_controls(self):
        box = ttk.Frame(self)
        box.pack()
        self.mx, self.my = tk.DoubleVar(value=0.5), tk.DoubleVar(value=0.5)
        self.mock_gesture = "NONE"
        for label in ("POINT", "PINCH", "TWO_FINGERS", "OPEN_PALM", "FIST", "THUMB_UP", "THUMB_DOWN", "NONE"):
            ttk.Button(box, text=label, command=lambda g=label: self.send_mock(g)).pack(side="left", padx=1)
        for variable in (self.mx, self.my):
            ttk.Scale(self, from_=0, to=1, variable=variable, command=lambda value: self.send_mock(self.mock_gesture)).pack(fill="x", padx=40)

    def send_mock(self, gesture):
        self.mock_gesture = gesture
        self.runner.commands.put(("sample", {"gesture": "NONE" if gesture == "PINCH" else gesture,
            "position": (self.mx.get(), self.my.get()), "detected": gesture != "NONE",
            "pinch_ratio": 0.15 if gesture == "PINCH" else 0.8}))

    def start(self):
        self.runner.start()
        self.runner.commands.put(("mode", self.mode.get()))
        self.enabled.set(False)
        self.start_button.configure(state="disabled")
        self.enable_button.configure(state="disabled")
        self.status.set("Starting — controls disabled")

    def enable(self):
        self.runner.commands.put(("enabled", self.enabled.get()))
        self.status.set("Controls enabled" if self.enabled.get() else "Tracking — controls disabled")

    def change_mode(self, event=None):
        self.enabled.set(False)
        self.runner.commands.put(("mode", self.mode.get()))
        self.status.set("Mode changed — controls disabled")

    def stop(self):
        self.enabled.set(False)
        self.enable_button.configure(state="disabled")
        self.runner.stop()
        self.status.set("Stopping — controls disabled")

    def close(self):
        self.closing = True
        self.stop()

    def append_log(self, message):
        self.log.append(message)

    def poll(self):
        for _ in range(100):
            try:
                kind, value = self.runner.events.get_nowait()
            except queue.Empty:
                break
            if kind in ("log", "error"):
                self.append_log(value)
                if kind == "error":
                    self.status.set(value)
            if kind == "status":
                self.status.set(value)
                if not self.closing and not self.runner.stop_event.is_set():
                    self.enable_button.configure(state="normal")
            elif kind == "sample":
                self.gesture.set(value)
            elif kind == "stopped":
                self.enabled.set(False)
                self.enable_button.configure(state="disabled")
                self.start_button.configure(state="normal")
                if not self.status.get().startswith("Controls stopped:"):
                    self.status.set("Stopped")
        try:
            frame = self.runner.frames.get_nowait()
            self.preview.show_frame(frame)
        except queue.Empty:
            pass
        except Exception as error:
            import logging
            logging.exception("Camera preview failed")
            self.append_log(f"Preview error: {error}")
            self.stop()
        if self.closing and not (self.runner.thread and self.runner.thread.is_alive()):
            self.destroy()
            return
        self.after(30, self.poll)

    def report_callback_exception(self, exception_type, value, traceback):
        import logging
        logging.error("GUI callback failed", exc_info=(exception_type, value, traceback))
        self.stop()
        self.status.set(f"Interface error: {value}")
        self.append_log(f"Interface error: {value}; see logs/gestura.log")
