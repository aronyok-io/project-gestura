"""Exercise the real Tk window lifecycle on the Windows CI runner."""
import sys
import time
import unittest


@unittest.skipUnless(sys.platform == "win32", "Windows GUI check")
class InterfaceTests(unittest.TestCase):
    def test_start_stop_and_close(self):
        from interface.app import App
        app = App(mock=True)
        def pump_until(predicate):
            deadline = time.monotonic() + 5
            while not predicate() and time.monotonic() < deadline:
                app.update()
                time.sleep(0.01)
            self.assertTrue(predicate())
        try:
            app.update()
            app.start()
            pump_until(lambda: str(app.enable_button.cget("state")) == "normal")
            self.assertFalse(app.enabled.get())
            app.stop()
            pump_until(lambda: str(app.start_button.cget("state")) == "normal")
            self.assertFalse(app.runner.thread.is_alive())
        finally:
            app.runner.stop()
            if app.runner.thread:
                app.runner.thread.join(2)
            app.destroy()
