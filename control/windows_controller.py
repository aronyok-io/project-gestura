"""Windows-only backend. Importing this module does not import Windows libraries."""
import math
import sys


class WindowsController:
    def __init__(self, emit=None, smoothing=0.35):
        if sys.platform != "win32":
            raise RuntimeError("Desktop control currently requires Windows. Use --mock on Fedora.")
        import pyautogui
        self.mouse = pyautogui
        self.mouse.FAILSAFE = True
        self.mouse.PAUSE = 0.01
        self.width, self.height = self.mouse.size()
        self.emit = emit or (lambda message: None)
        self.smoothing = smoothing
        self.com = None
        self.audio = None
        self.audio_error = False
        self.previous = None

    def reset(self):
        self.previous = None

    def move(self, x, y):
        if not math.isfinite(x) or not math.isfinite(y):
            return
        # Leave a margin so gesture movement cannot place the pointer in a fail-safe corner.
        target = (max(1, min(self.width - 2, round(x * (self.width - 1)))),
                  max(1, min(self.height - 2, round(y * (self.height - 1)))))
        if self.previous is None:
            p = self.mouse.position()
            self.previous = (p.x, p.y)
        self.previous = tuple(a + (b - a) * self.smoothing for a, b in zip(self.previous, target))
        self.mouse.moveTo(*(round(v) for v in self.previous), duration=0)

    def check_failsafe(self):
        self.mouse.failSafeCheck()

    def click(self):
        self.mouse.click()
        self.emit("Left click")

    def scroll(self, amount):
        self.mouse.scroll(amount)
        self.emit(f"Scroll {amount}")

    def media(self, action):
        if self.audio_error:
            return
        try:
            if self.audio is None:
                from ctypes import cast, POINTER
                import comtypes
                comtypes.CoInitialize()
                self.com = comtypes
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                speakers = AudioUtilities.GetSpeakers()
                if hasattr(speakers, "EndpointVolume"):
                    self.audio = speakers.EndpointVolume
                else:
                    self.audio = cast(speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))
            if action in ("mute", "unmute"):
                self.audio.SetMute(int(action == "mute"), None)
            else:
                delta = 0.05 if action == "volumeup" else -0.05
                level = max(0.0, min(1.0, self.audio.GetMasterVolumeLevelScalar() + delta))
                self.audio.SetMasterVolumeLevelScalar(level, None)
            self.emit(action)
        except Exception as error:
            self.audio_error = True
            self.emit(f"Audio unavailable; mouse control still works: {error}")

    def close(self):
        # Release COM references and balance initialization on the owning worker thread.
        self.audio = None
        if self.com is not None:
            self.com.CoUninitialize()
            self.com = None
