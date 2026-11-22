"""No hardware imports: exercise detector boundaries and real protocol fixture."""
import ast
import json
import math
import statistics
import unittest
from collections import deque
from pathlib import Path

ROOT = Path(__file__).parent
source = ast.parse((ROOT / 'motion_live.py').read_text())
names = {'norm', 'rms', 'HeadDetector', 'hand_features', 'HandDetector'}
subset = ast.Module(body=[n for n in source.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names], type_ignores=[])

class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.ns = dict(math=math, statistics=statistics, deque=deque,
                       PERIOD=.04, MAX_GAP=.12,
                       emit=lambda kind, **fields: self.events.append(dict(type=kind, **fields)))
        exec(compile(subset, 'detector_subset', 'exec'), self.ns)

    def test_real_session_events(self):
        events = [json.loads(s) for s in (ROOT / 'examples/head_session.jsonl').read_text().splitlines()]
        self.assertEqual([e['action'] for e in events if e['type'] == 'head_event'], ['confirm','next','undo'])
        self.assertEqual([e['seq'] for e in events], list(range(1,len(events)+1)))
        self.assertFalse(any(e['type'] in ('sensor_fault','fatal') for e in events))

    def test_head_templates_once(self):
        for action, a, b in [('confirm',(3,0,0),(-3,0,0)),
                             ('next',(0,2,-2),(0,-2,2)),
                             ('undo',(0,-2,2),(0,2,-2))]:
            self.events.clear()
            detector = self.ns['HeadDetector']()
            t = 0
            for g, count in [((0,0,0),10),(a,8),(b,8),((0,0,0),30)]:
                for _ in range(count):
                    detector.update(t, (0,0,9.8,*g)); t += .04
            self.assertEqual([e['action'] for e in self.events], [action])

    def test_gap_cannot_complete_head_event(self):
        d = self.ns['HeadDetector']()
        for i in range(10): d.update(i*.04, (0,0,9.8,3,0,0))
        for i in range(10): d.update(2+i*.04, (0,0,9.8,-3,0,0))
        for i in range(20): d.update(2.4+i*.04, (0,0,9.8,0,0,0))
        self.assertEqual(self.events, [])

    def test_hand_fault_reset_keeps_counts(self):
        d = self.ns['HandDetector']('auto'); d.strokes=4; d.cycles=2
        d.stroke=[('unfinished',)]; d.reset()
        self.assertEqual((d.strokes,d.cycles,d.stroke,d.label),(4,2,[],'unknown'))

    def test_features_reject_large_gap(self):
        rows=[(i*.04, (0,0,9.8,0,1,0),.1) for i in range(51)]
        rows[25]=(rows[25][0]+.2,rows[25][1],.1)
        self.assertIsNone(self.ns['hand_features'](rows))

if __name__ == '__main__':
    unittest.main()
