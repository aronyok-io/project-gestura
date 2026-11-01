class Camera:
    def __init__(self, index=0):
        import cv2
        self.cv2 = cv2
        self.capture = cv2.VideoCapture(index)
        if not self.capture.isOpened():
            self.close()
            raise RuntimeError("Webcam could not be opened. Check permissions and other camera apps.")

    def read(self):
        success, frame = self.capture.read()
        if not success:
            raise RuntimeError("Webcam disconnected or frame capture failed.")
        return self.cv2.flip(frame, 1)

    def close(self):
        self.capture.release()
