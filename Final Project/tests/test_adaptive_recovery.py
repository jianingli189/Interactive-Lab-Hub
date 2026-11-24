import sys
import types
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from sensor_recovery import RecoveryReader
class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.now=0.;self.events=[];self.bad=False;self.reads=0;self.config=(1,2)
        self.hw=types.SimpleNamespace(configuration=lambda item:self.config,read_one=self.read)
        self.r=RecoveryReader(self.hw,lambda k,**v:self.events.append((k,v)),lambda:self.now)
        self.item={'name':'RH','baseline':(1,2)}
    def read(self,*args):
        self.reads+=1
        if self.bad:raise OSError(121,'test')
        return self.now,(1,2,3,4,5,6)
    def test_recovers_after_more_than_three_failures_and_validates_samples(self):
        self.bad=True
        for delay in (.5,1,2,5,5,5):
            self.assertIsNone(self.r.read('RH',self.item,0));before=self.reads
            self.now+=delay/2;self.assertIsNone(self.r.read('RH',self.item,0));self.assertEqual(self.reads,before)
            self.now+=delay/2
        self.bad=False
        for _ in range(4):self.assertIsNone(self.r.read('RH',self.item,0));self.now+=.04
        self.assertIsNotNone(self.r.read('RH',self.item,0))
        self.assertTrue(any(k=='sensor_recovered' for k,v in self.events))
        self.now+=31;self.r.read('RH',self.item,0);self.assertEqual(self.r.states['RH']['failures'],0)
    def test_only_restore_on_configuration_difference(self):
        calls=[]
        self.r.restore=lambda item,actual:(calls.append(actual),setattr(self,'config',(1,2)))
        self.bad=True;self.r.read('RH',self.item,0);self.bad=False;self.now=1
        self.r.read('RH',self.item,0);self.assertEqual(calls,[])
        self.config=(0,0);self.now+=1;self.r.read('RH',self.item,0);self.assertEqual(calls,[(0,0)])

    def test_bno_invalid_mode_exception_reconfigures(self):
        calls=[]
        def configuration(item):
            if self.config != (160,8):
                raise RuntimeError('RH bad state: mode=0')
            return self.config
        self.item['baseline']=(160,8)
        self.hw.configuration=configuration
        self.hw.rh_state=lambda item:(0,160,0,1,0,0,0)
        def configure(item):
            calls.append('configure')
            self.config=(160,8)
        self.hw.rh_configure=configure
        self.assertIsNone(self.r.read('RH',self.item,0))
        self.now=1
        for _ in range(4):
            self.assertIsNone(self.r.read('RH',self.item,0))
            self.now+=.04
        self.assertIsNotNone(self.r.read('RH',self.item,0))
        self.assertEqual(calls,['configure'])

    def test_bno_wrong_identity_never_written(self):
        def configuration(item):
            raise RuntimeError('RH bad state')
        self.hw.configuration=configuration
        self.hw.rh_state=lambda item:(0,0,0,1,0,0,0)
        calls=[]
        self.hw.rh_configure=lambda item:calls.append(True)
        self.r.read('RH',self.item,0)
        self.now=1
        self.r.read('RH',self.item,0)
        self.assertEqual(calls,[])

    def test_warmup_does_not_check_configuration_every_sample(self):
        calls=[]
        self.hw.configuration=lambda item:(calls.append(True) or self.config)
        for _ in range(5):
            self.r.read('RH',self.item,0)
            self.now+=.04
        self.assertEqual(len(calls),1)
        self.now=1.1
        self.r.read('RH',self.item,0)
        self.assertEqual(len(calls),2)

    def test_fault_reports_sample_stage(self):
        self.bad=True
        self.r.read('RH',self.item,0)
        self.assertIn('stage=read_sample',self.events[-1][1]['message'])
