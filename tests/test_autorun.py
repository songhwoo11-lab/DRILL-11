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


if __name__ == '__main__':
    unittest.main()
