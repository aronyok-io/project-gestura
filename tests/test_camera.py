import sys
import unittest
from unittest.mock import Mock, patch
from vision.camera import Camera


class CameraTests(unittest.TestCase):
    def test_open_failure_releases_device(self):
        cv2 = Mock()
        cv2.VideoCapture.return_value.isOpened.return_value = False
        with patch.dict(sys.modules, {'cv2': cv2}):
            with self.assertRaisesRegex(RuntimeError, 'Webcam could not'):
                Camera()
        cv2.VideoCapture.return_value.release.assert_called_once()

    def test_frame_failure_is_reported(self):
        cv2 = Mock()
        capture = cv2.VideoCapture.return_value
        capture.read.return_value = (False, None)
        with patch.dict(sys.modules, {'cv2': cv2}):
            camera = Camera(1)
            with self.assertRaisesRegex(RuntimeError, 'disconnected'):
                camera.read()
            camera.close()
        capture.release.assert_called_once()
