import unittest
from pathlib import Path
from unittest.mock import patch

class DemoTests(unittest.TestCase):
    def test_movement_only_and_no_fake_counts(self):
        class Base:
            def __init__(self):
                self.reset()
            def reset(self):
                self.rows=[]; self.label='unknown'; self.label_hits=0; self.pending_label=None
        events=[]
        source_globals={'HandDetector':Base, 'emit':lambda kind,**kw: events.append((kind,kw)),
                        'hand_features':lambda rows: {'rh_rms':0.5,'acc_sd':0.1}}
        exec('def main(): pass',source_globals)
        path=Path(__file__).parents[1]/'motion_demo.py'
        namespace={'__name__':'demo_test','__file__':str(path)}
        with patch('runpy.run_path',return_value={'main':source_globals['main']}):
            exec(compile(path.read_text(),str(path),'exec'),namespace)
        d=source_globals['HandDetector']()
        def feed(names, moving=True):
            for i in range(30):
                value=(0,0,9.8,1 if moving else 0,0,0)
                d.update_available({n:(i*.04,value) for n in names})
        feed(['RH'])
        d.classify();d.classify();self.assertEqual(d.label,'moving')
        feed(['LH'])
        d.classify();d.classify();self.assertEqual(d.label,'moving')
        d.update_available({});d.classify();self.assertEqual(d.label,'unknown')
        feed(['LH'],False)
        d.classify();self.assertEqual(d.label,'idle')
        d.update_flip(0,());d.update_twist(0,(),0);self.assertEqual(events,[])
        source_globals['emit']('head_event',action='next')
        self.assertEqual(events[-1],('head_event',{'action':'next','recognition_mode':'demo'}))
