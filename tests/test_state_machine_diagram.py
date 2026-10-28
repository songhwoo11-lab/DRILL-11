import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


class StateMachineDiagramTests(unittest.TestCase):
    def test_diagram_is_valid_and_contains_all_states_and_transitions(self):
        root = ET.parse(Path(__file__).parents[1] / 'state_machine.svg').getroot()
        text = ' '.join(element.text or '' for element in root.iter())

        for state in ('IDLE', 'RUN', 'SLEEP', 'AUTORUN'):
            with self.subTest(state=state):
                self.assertIn(state, text)

        for label in ('A 누름', 'A 재입력', '좌/우 누름', '5초 경과', 'Space', '경계'):
            with self.subTest(label=label):
                self.assertIn(label, text)


if __name__ == '__main__':
    unittest.main()
