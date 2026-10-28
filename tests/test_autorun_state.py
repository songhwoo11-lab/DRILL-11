import unittest
from unittest.mock import patch

from autorun_state import AutoRunState
from boy import Boy


class AutoRunStateIntegrationTests(unittest.TestCase):
    def setUp(self):
        with patch('boy.load_image'):
            self.boy = Boy()

    def test_boy_owns_a_dedicated_autorun_state(self):
        self.assertIsInstance(self.boy.auto_run_state, AutoRunState)
        self.assertIs(self.boy.auto_run_state.boy, self.boy)

    def test_state_class_returns_to_run_through_machine_transition(self):
        self.boy.start_auto_run()
        self.assertIsNotNone(self.boy.auto_run_state.deadline)

        self.boy.auto_run_state.return_to_run()

        self.assertEqual(self.boy.state, 'RUN')
        self.assertIsNone(self.boy.auto_run_state.deadline)

    def test_state_class_expiry_transitions_machine_to_idle(self):
        self.boy.start_auto_run()
        self.boy.auto_run_state.start(now=10)

        with patch('autorun_state.time.monotonic', return_value=15):
            self.boy.update()

        self.assertEqual(self.boy.state, 'IDLE')
        self.assertIsNone(self.boy.auto_run_state.deadline)


if __name__ == '__main__':
    unittest.main()
