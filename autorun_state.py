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
        self.boy.run_frame = (self.boy.run_frame + 1) % 8
        self.boy.x += (
            self.boy.dir
            * self.boy.RUN_SPEED
            * self.SPEED_MULTIPLIER
        )
        half_width = (
            self.boy.HALF_SPRITE_WIDTH * self.SCALE_MULTIPLIER
        )
        min_x = half_width
        max_x = self.boy.SCREEN_WIDTH - half_width
        if self.boy.x <= min_x or self.boy.x >= max_x:
            self.boy.x = max(min_x, min(self.boy.x, max_x))
            self.boy.dir = -self.boy.dir
            self.boy.face_dir = self.boy.dir
        return self.is_expired(now)
