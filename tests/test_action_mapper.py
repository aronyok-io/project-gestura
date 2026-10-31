import unittest
from control.action_mapper import ActionMapper
from control.mock_controller import MockController
from core.state_manager import StateManager


def sample(gesture='POINT', ratio=0.8, detected=True, y=0.5):
    return dict(gesture=gesture, position=(0.5, y), detected=detected, pinch_ratio=ratio)


class ActionTests(unittest.TestCase):
    def setUp(self):
        self.controller = MockController()
        self.mapper = ActionMapper(self.controller)
        self.state = StateManager(enabled=True)

    def process(self, data, *times):
        for t in times:
            self.mapper.process(data, self.state, t)

    def test_disabled_has_no_actions(self):
        self.state.enabled = False
        self.process(sample(ratio=0.1), 0, 1, 2)
        self.assertEqual(self.controller.actions, [])

    def test_first_frame_pinching_then_hold(self):
        self.process(sample(ratio=0.1), 0, 0.2, 0.5, 2)
        self.assertEqual(self.controller.actions, [('click',)])

    def test_hysteresis_and_release(self):
        self.process(sample(ratio=0.1), 0, 0.2)
        self.process(sample(ratio=0.35), 0.3, 0.5)
        self.process(sample(ratio=0.1), 0.6)
        self.assertEqual(self.controller.actions, [('click',)])
        self.process(sample(ratio=0.8), 0.7)
        self.process(sample(ratio=0.1), 0.8, 1.0)
        self.assertEqual(self.controller.actions, [('click',), ('click',)])

    def test_short_pinch_is_ignored(self):
        self.process(sample(ratio=0.1), 0)
        self.process(sample(), 0.05)
        self.assertEqual(self.controller.actions, [])

    def test_no_hand_clears_pending_click(self):
        self.process(sample(ratio=0.1), 0)
        self.process(sample(detected=False), 0.05)
        self.process(sample(ratio=0.1), 0.2)
        self.assertEqual(self.controller.actions, [])
        self.process(sample(ratio=0.1), 0.4)
        self.assertEqual(self.controller.actions, [('click',)])

    def test_movement_requires_confirmation(self):
        self.process(sample(), 0)
        self.assertEqual(self.controller.actions, [])
        self.process(sample(), 0.2)
        self.assertEqual(self.controller.actions, [('move', 0.5, 0.5)])
        self.process(sample(detected=False), 0.3)
        self.process(sample(), 0.4)
        self.assertEqual(len(self.controller.actions), 1)

    def test_scroll_does_not_move_cursor(self):
        self.process(sample('TWO_FINGERS'), 0, 0.2)
        self.process(sample('TWO_FINGERS', y=0.45), 0.3)
        self.assertEqual(self.controller.actions, [('scroll', 5)])

    def test_media_one_action_per_hold(self):
        self.state.mode = 'Media'
        self.process(sample('THUMB_UP'), 0, 0.2, 1, 2)
        self.assertEqual(self.controller.actions, [('media', 'volumeup')])
        self.process(sample('NONE'), 2.1, 2.3)
        self.process(sample('THUMB_UP'), 2.4, 2.6)
        self.assertEqual(len(self.controller.actions), 2)

    def test_mode_switch_disables(self):
        self.state.set_mode('Media')
        self.assertFalse(self.state.enabled)
        with self.assertRaises(ValueError):
            self.state.set_mode('Bad')

    def test_brief_media_uncertainty_does_not_repeat(self):
        self.state.mode = 'Media'
        self.process(sample('THUMB_UP'), 0, 0.2)
        self.process(sample('NONE'), 0.3)
        self.process(sample('THUMB_UP'), 0.35, 0.5)
        self.assertEqual(self.controller.actions, [('media', 'volumeup')])
