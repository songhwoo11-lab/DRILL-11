import unittest
from unittest.mock import patch
from types import SimpleNamespace

import main
from boy import Boy


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

    def test_repeated_keydown_does_not_restart_autorun_timer(self):
        event = SimpleNamespace(type=main.SDL_KEYDOWN, key=main.SDLK_a)
        main.handle_events([event])
        deadline = self.boy.auto_run_state.deadline

        main.handle_events([event])

        self.assertEqual(self.boy.auto_run_state.deadline, deadline)


if __name__ == '__main__':
    unittest.main()
