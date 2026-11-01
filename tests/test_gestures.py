import unittest
from types import SimpleNamespace as NS
from vision.gesture_recognizer import pinch_ratio, sample_from_result


class VisionTests(unittest.TestCase):
    def hand(self):
        hand = [NS(x=0.5, y=0.5) for _ in range(21)]
        hand[0].y = 0.8
        hand[9].y = 0.5
        hand[4].x = 0.51
        return hand

    def test_missing_hand(self):
        s = sample_from_result(NS(hand_landmarks=[], gestures=[]), 640, 480)
        self.assertFalse(s['detected'])
        self.assertIsNone(s['position'])

    def test_label_translation_and_confidence(self):
        result = NS(hand_landmarks=[self.hand()], gestures=[[NS(category_name='Victory', score=0.9)]])
        self.assertEqual(sample_from_result(result, 640, 480)['gesture'], 'TWO_FINGERS')
        result.gestures[0][0].score = 0.1
        self.assertEqual(sample_from_result(result, 640, 480)['gesture'], 'NONE')

    def test_pinch_is_scale_independent(self):
        hand = self.hand()
        self.assertAlmostEqual(pinch_ratio(hand, 640, 480), pinch_ratio(hand, 1280, 960))
        hand[0].y = hand[9].y
        self.assertIsNone(pinch_ratio(hand, 640, 480))
