import importlib.util
import json
from pathlib import Path
import queue
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bridge'))
from sensor_bridge import Hub
from utensil_mqtt import normalize_state

class BridgeTests(unittest.TestCase):
    def test_failed_and_missing_sensor_unknown(self):
        state = normalize_state({'utensils': {'knife': {'present': True, 'valid': False}}}, 123)
        self.assertIsNone(state['utensils']['knife']['present'])
        self.assertFalse(state['utensils']['spatula']['valid'])

    def test_legacy_is_not_verified(self):
        state = normalize_state({'utensils': {'knife': {'present': False}}}, 123)
        self.assertFalse(state['utensils']['knife']['healthKnown'])

    def test_correct_report(self):
        state = normalize_state({'utensils': {'knife': {'present': False, 'valid': True}}}, 123)
        self.assertEqual(state['utensils']['knife']['present'], False)
        self.assertTrue(state['utensils']['knife']['healthKnown'])

    def test_slow_client_closed(self):
        h=Hub('replay'); q=queue.Queue(maxsize=1); h.add(q)
        h.broadcast('state', {}); h.broadcast('state', {})
        self.assertIsNone(q.get_nowait()); self.assertNotIn(q,h.clients)

    def test_real_motion_fixture(self):
        h=Hub('replay'); h.new_session()
        for line in (ROOT/'bridge/fixtures/head_session.jsonl').read_text().splitlines(): h.line(line)
        self.assertEqual(h.invalid_lines,0)
        self.assertEqual(h.latest_state['sensors']['HF'],True)
        self.assertNotIn('head_event', h.hello())

if __name__ == '__main__': unittest.main()
