import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from control.windows_controller import WindowsController


class WindowsControllerTests(unittest.TestCase):
    def setUp(self):
        self.mouse = Mock()
        self.mouse.size.return_value = (1920, 1080)
        self.mouse.position.return_value = SimpleNamespace(x=960, y=540)
        self.modules = patch.dict(sys.modules, {'pyautogui': self.mouse})
        self.platform = patch('sys.platform', 'win32')
        self.modules.start()
        self.platform.start()
        self.addCleanup(self.modules.stop)
        self.addCleanup(self.platform.stop)
        self.controller = WindowsController()

    def test_init_does_not_require_audio(self):
        self.assertIsNone(self.controller.audio)
        self.assertIsNone(self.controller.com)
        self.assertTrue(self.mouse.FAILSAFE)

    def test_move_bounds_and_smoothing_from_current_position(self):
        self.controller.move(100, -100)
        x, y = self.mouse.moveTo.call_args.args
        self.assertGreater(x, 960)
        self.assertLess(x, 1920)
        self.assertGreater(y, 0)
        self.assertLess(y, 540)
        self.controller.reset()
        self.assertIsNone(self.controller.previous)

    def test_invalid_coordinates_ignored(self):
        self.controller.move(float('nan'), 0.5)
        self.mouse.moveTo.assert_not_called()

    def test_failsafe_propagates_to_worker(self):
        self.mouse.click.side_effect = RuntimeError('Fail-safe triggered')
        with self.assertRaisesRegex(RuntimeError, 'Fail-safe'):
            self.controller.click()

    def test_audio_failure_does_not_disable_mouse(self):
        with patch.dict(sys.modules, {'comtypes': None}):
            self.controller.media('mute')
        self.assertTrue(self.controller.audio_error)
        self.controller.click()
        self.mouse.click.assert_called_once()

    def test_audio_volume_clamps_and_mute(self):
        audio = Mock()
        self.controller.audio = audio
        audio.GetMasterVolumeLevelScalar.return_value = 0.99
        self.controller.media('volumeup')
        audio.SetMasterVolumeLevelScalar.assert_called_with(1.0, None)
        audio.GetMasterVolumeLevelScalar.return_value = 0.01
        self.controller.media('volumedown')
        audio.SetMasterVolumeLevelScalar.assert_called_with(0.0, None)
        self.controller.media('mute')
        audio.SetMute.assert_called_with(1, None)
        self.controller.media('unmute')
        audio.SetMute.assert_called_with(0, None)

    def test_failsafe_without_mouse_action(self):
        self.mouse.failSafeCheck.side_effect = RuntimeError('Fail-safe triggered')
        with self.assertRaisesRegex(RuntimeError, 'Fail-safe'):
            self.controller.check_failsafe()
        self.mouse.moveTo.assert_not_called()
        self.mouse.click.assert_not_called()
