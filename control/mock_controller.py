class MockController:
    """Records commands without touching the desktop."""
    def __init__(self, emit=None):
        self.emit = emit or (lambda message: None)
        self.actions = []

    def close(self):
        pass

    def reset(self):
        pass

    def record(self, *action):
        self.actions.append(action)
        if len(self.actions) > 1000:
            del self.actions[:500]
        self.emit(str(action))

    def move(self, x, y):
        self.record("move", x, y)

    def click(self):
        self.record("click")

    def scroll(self, amount):
        self.record("scroll", amount)

    def media(self, action):
        self.record("media", action)
