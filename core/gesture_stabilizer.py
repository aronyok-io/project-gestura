class GestureStabilizer:
    """Require a continuous gesture for a measured duration, independent of FPS."""
    def __init__(self, delay=0.12):
        self.delay = delay
        self.reset()

    def reset(self):
        self.candidate = "NONE"
        self.since = None

    def update(self, gesture, now):
        if gesture != self.candidate or self.since is None:
            self.candidate, self.since = gesture, now
        return gesture if now - self.since >= self.delay else "NONE"
