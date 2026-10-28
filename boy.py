from math import pi
import time

from autorun_state import AutoRunState
from pico2d import load_image
from transitions import Machine


class Boy:
    SCREEN_WIDTH = 800
    HALF_SPRITE_WIDTH = 50
    RUN_SPEED = 5
    SLEEP_GROUND_Y = 61
    # Per-frame offsets keep the rotated sprite's lowest pixel on the grass surface.
    SLEEP_GROUND_OFFSETS = {
        1: (16, 16, 16, 18, 17, 16, 18, 18),
        -1: (14, 14, 14, 16, 15, 14, 16, 16),
    }

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.run_frame = 0
        self.face_dir = 1
        self.dir = 1
        self.idle_started_at = time.monotonic()
        self.image = load_image('animation_sheet.png')
        self.run_image = load_image('run_animation.png')
        self.auto_run_state = AutoRunState(self)
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'SLEEP', 'AUTORUN'],
            initial='IDLE',
            auto_transitions=False,
            transitions=[
                {'trigger': 'fall_asleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {
                    'trigger': 'start_auto_run',
                    'source': ['IDLE', 'RUN', 'SLEEP', 'AUTORUN'],
                    'dest': 'AUTORUN',
                    'after': 'begin_auto_run',
                },
                {
                    'trigger': 'stop_auto_run',
                    'source': 'AUTORUN',
                    'dest': 'IDLE',
                    'after': ['end_auto_run', 'start_idle_timer'],
                },
                {
                    'trigger': 'start_running',
                    'source': ['IDLE', 'SLEEP'],
                    'dest': 'RUN',
                    'after': 'reset_run_frame',
                },
                {
                    'trigger': 'stop_running',
                    'source': 'RUN',
                    'dest': 'IDLE',
                    'after': 'start_idle_timer',
                },
                {
                    'trigger': 'wake_up',
                    'source': 'SLEEP',
                    'dest': 'IDLE',
                    'after': 'start_idle_timer',
                },
            ],
        )

    def begin_auto_run(self):
        self.run_frame = 0
        self.auto_run_state.start()

    def end_auto_run(self):
        self.auto_run_state.cancel()

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8
            if time.monotonic() - self.idle_started_at >= 5:
                self.fall_asleep()
        elif self.state == 'RUN':
            self.run_frame = (self.run_frame + 1) % 8
            self.x += self.dir * self.RUN_SPEED
            min_x = self.HALF_SPRITE_WIDTH
            max_x = self.SCREEN_WIDTH - self.HALF_SPRITE_WIDTH
            if self.x <= min_x or self.x >= max_x:
                self.x = max(min_x, min(self.x, max_x))
                self.stop_running()
        elif self.state == 'AUTORUN':
            if self.auto_run_state.update():
                self.stop_auto_run()

    def start_idle_timer(self):
        self.idle_started_at = time.monotonic()

    def reset_run_frame(self):
        self.run_frame = 0

    def draw(self):
        if self.state in ('RUN', 'AUTORUN'):
            size = 100
            if self.state == 'AUTORUN':
                size *= self.auto_run_state.SCALE_MULTIPLIER
            if self.dir == 1:
                self.run_image.clip_draw(
                    self.run_frame * 100, 0, 100, 100, self.x, self.y, size, size
                )
            else:
                self.run_image.clip_composite_draw(
                    self.run_frame * 100, 0, 100, 100, 0, 'h',
                    self.x, self.y, size, size,
                )
            return

        if self.face_dir == 1:
            source_y = 300
            angle = pi / 2
            direction = 1
        else:
            source_y = 200
            angle = -pi / 2
            direction = -1

        if self.state == 'SLEEP':
            y = self.SLEEP_GROUND_Y + self.SLEEP_GROUND_OFFSETS[direction][self.frame] // 2
            self.image.clip_composite_draw(
                self.frame * 100, source_y, 100, 100, angle, '', self.x, y, 100, 100
            )
        else:
            self.image.clip_draw(self.frame * 100, source_y, 100, 100, self.x, self.y)
