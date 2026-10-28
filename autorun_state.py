import time


class AutoRunState:
    DURATION = 5.0
    SPEED_MULTIPLIER = 2.0
    SCALE_MULTIPLIER = 1.5

    def __init__(self, boy):
        self.boy = boy
        self.deadline = None

    def start(self, now=None):
        if now is None:
            now = time.monotonic()
        self.deadline = now + self.DURATION

    def cancel(self):
        self.deadline = None

    def is_expired(self, now=None):
        if self.deadline is None:
            return False
        if now is None:
            now = time.monotonic()
        return now >= self.deadline

    def update(self, now=None):
        return self.is_expired(now)
