import time
import unittest
from core.runner import Runner


class RunnerTests(unittest.TestCase):
    def wait_for(self, runner, kind):
        end = time.monotonic() + 2
        while time.monotonic() < end:
            event, value = runner.events.get(timeout=2)
            if event == kind:
                return value
        self.fail('Worker event missing: ' + kind)

    def test_mock_start_stop_restart(self):
        runner = Runner(mock=True)
        try:
            runner.start()
            self.wait_for(runner, 'status')
            runner.commands.put(('enabled', True))
            runner.commands.put(('sample', dict(gesture='POINT', position=(0.5, 0.5), detected=True, pinch_ratio=0.8)))
            self.assertIn('move', self.wait_for(runner, 'log'))
            runner.stop()
            runner.thread.join(2)
            self.assertFalse(runner.thread.is_alive())
            self.wait_for(runner, 'stopped')
            runner.commands.put(('enabled', True))  # stale command must be discarded
            runner.start()
            self.wait_for(runner, 'status')
            runner.stop()
            runner.thread.join(2)
            self.assertFalse(runner.thread.is_alive())
        finally:
            runner.stop()
            runner.thread.join(2)
