import unittest
from unittest.mock import patch
from types import SimpleNamespace

import main
from boy import Boy


class RecordingImage:
    def __init__(self):
        self.draw_calls = []

    def clip_draw(self, *args):
        self.draw_calls.append(args)

    def clip_composite_draw(self, *args):
        self.draw_calls.append(args)


class AutoRunInputTests(unittest.TestCase):
    def setUp(self):
        with patch('boy.load_image'):
            self.boy = Boy()
        main.boy = self.boy
        main.pressed_keys.clear()
        main.pressed_directions.clear()
        main.running = True

    def tearDown(self):
        main.pressed_keys.clear()
        main.pressed_directions.clear()

    def test_a_key_starts_autorun_from_idle(self):
        event = SimpleNamespace(type=main.SDL_KEYDOWN, key=main.SDLK_a)

        main.handle_events([event])

        self.assertEqual(self.boy.state, 'AUTORUN')
        self.assertIsNotNone(self.boy.auto_run_state.deadline)

    def test_a_key_starts_autorun_from_run(self):
        self.boy.start_running()
        event = SimpleNamespace(type=main.SDL_KEYDOWN, key=main.SDLK_a)

        main.handle_events([event])

        self.assertEqual(self.boy.state, 'AUTORUN')

    def test_a_key_starts_autorun_from_sleep(self):
        self.boy.fall_asleep()
        event = SimpleNamespace(type=main.SDL_KEYDOWN, key=main.SDLK_a)

        main.handle_events([event])

        self.assertEqual(self.boy.state, 'AUTORUN')

    def test_repeated_keydown_does_not_restart_autorun_timer(self):
        event = SimpleNamespace(type=main.SDL_KEYDOWN, key=main.SDLK_a)
        main.handle_events([event])
        deadline = self.boy.auto_run_state.deadline

        main.handle_events([event])

        self.assertEqual(self.boy.auto_run_state.deadline, deadline)

    def test_direction_key_returns_autorun_to_run(self):
        self.boy.start_auto_run()
        event = SimpleNamespace(type=main.SDL_KEYDOWN, key=main.SDLK_LEFT)

        main.handle_events([event])

        self.assertEqual(self.boy.state, 'RUN')
        self.assertEqual(self.boy.dir, -1)
        self.assertEqual(self.boy.face_dir, -1)
        self.assertIsNone(self.boy.auto_run_state.deadline)

    def test_cancelled_autorun_deadline_cannot_change_later_state(self):
        self.boy.start_auto_run()
        self.boy.auto_run_state.start(now=10)
        self.boy.start_running()

        with patch('autorun_state.time.monotonic', return_value=20):
            self.boy.update()

        self.assertEqual(self.boy.state, 'RUN')
        self.assertIsNone(self.boy.auto_run_state.deadline)

    def test_idle_sleep_timer_restarts_after_autorun_expires(self):
        self.boy.start_auto_run()
        self.boy.auto_run_state.start(now=10)
        with patch('autorun_state.time.monotonic', return_value=15):
            self.boy.update()

        with patch('autorun_state.time.monotonic', return_value=19.9):
            self.boy.update()
        self.assertEqual(self.boy.state, 'IDLE')

        with patch('autorun_state.time.monotonic', return_value=20):
            self.boy.update()
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_autorun_sprite_is_larger_than_run_sprite(self):
        image = RecordingImage()
        self.boy.run_image = image
        self.boy.start_running()
        self.boy.draw()
        run_size = image.draw_calls[-1][-2:]

        self.boy.start_auto_run()
        self.boy.draw()
        auto_run_size = image.draw_calls[-1][-2:]

        self.assertGreater(auto_run_size[0], run_size[0])
        self.assertGreater(auto_run_size[1], run_size[1])

    def test_autorun_moves_faster_than_run(self):
        self.boy.start_running()
        self.boy.update()
        run_distance = self.boy.x - 400

        self.boy.x = 400
        self.boy.start_auto_run()
        self.boy.update()
        auto_run_distance = self.boy.x - 400

        self.assertGreater(auto_run_distance, run_distance)

    def test_autorun_reverses_at_scaled_screen_boundary(self):
        self.boy.x = 790
        self.boy.dir = 1
        self.boy.start_auto_run()

        self.boy.update()

        self.assertEqual(self.boy.x, 725)
        self.assertEqual(self.boy.dir, -1)
        self.assertEqual(self.boy.face_dir, -1)

    def test_boundary_reversal_preserves_autorun_deadline(self):
        self.boy.x = 790
        self.boy.dir = 1
        self.boy.start_auto_run()
        self.boy.auto_run_state.start(now=10)
        deadline = self.boy.auto_run_state.deadline

        self.boy.auto_run_state.update(now=12)

        self.assertEqual(self.boy.state, 'AUTORUN')
        self.assertEqual(self.boy.auto_run_state.deadline, deadline)
        self.assertFalse(self.boy.auto_run_state.is_expired(now=14.9))
        self.assertTrue(self.boy.auto_run_state.is_expired(now=15))

    def test_autorun_expires_after_five_seconds_to_idle(self):
        self.boy.start_auto_run()
        self.boy.auto_run_state.start(now=10)

        with patch('autorun_state.time.monotonic', return_value=14.9):
            self.boy.update()
        self.assertEqual(self.boy.state, 'AUTORUN')

        with patch('autorun_state.time.monotonic', return_value=15):
            self.boy.update()

        self.assertEqual(self.boy.state, 'IDLE')
        self.assertIsNone(self.boy.auto_run_state.deadline)
        self.assertEqual(self.boy.idle_started_at, 15)

    def test_expiry_restores_idle_rendering_and_stops_auto_run_motion(self):
        idle_image = RecordingImage()
        run_image = RecordingImage()
        self.boy.image = idle_image
        self.boy.run_image = run_image
        self.boy.run_frame = 6
        self.boy.start_auto_run()
        self.boy.auto_run_state.start(now=10)
        self.boy.x = 400

        with patch('autorun_state.time.monotonic', return_value=15):
            self.boy.update()
        expired_x = self.boy.x
        self.boy.draw()

        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.x, expired_x)
        self.assertEqual(len(idle_image.draw_calls), 1)
        self.assertEqual(run_image.draw_calls, [])
        self.assertEqual(self.boy.run_frame, 0)


if __name__ == '__main__':
    unittest.main()
