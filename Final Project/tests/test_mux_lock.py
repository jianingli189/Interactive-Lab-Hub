import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from safe_mux import install
class Bus:
    def __init__(self): self.locked=False;self.fail=False
    def try_lock(self):
        if self.locked:return False
        self.locked=True;return True
    def unlock(self):self.locked=False
    def writeto(self,*args):
        if self.fail:raise OSError(121,'simulated mux write failure')
class LockTests(unittest.TestCase):
    def setUp(self):
        class Channel:pass
        module=types.SimpleNamespace(TCA9548A_Channel=Channel);install(module)
        self.ch=Channel();self.bus=Bus();self.ch.tca=types.SimpleNamespace(i2c=self.bus,address=0x70);self.ch.channel_switch=b'\x01'
    def test_failed_select_releases(self):
        self.bus.fail=True
        with self.assertRaises(OSError):self.ch.try_lock()
        self.assertFalse(self.bus.locked)
        self.bus.fail=False;self.assertTrue(self.ch.try_lock());self.ch.unlock();self.assertFalse(self.bus.locked)
    def test_failed_deselect_releases(self):
        self.ch.try_lock();self.bus.fail=True
        with self.assertRaises(OSError):self.ch.unlock()
        self.assertFalse(self.bus.locked)
    def test_busy_lock_bounded_without_unlocking_other_owner(self):
        self.bus.locked=True
        with patch('safe_mux.time.monotonic',side_effect=[0,1]):
            with self.assertRaises(TimeoutError):self.ch.try_lock()
        self.assertTrue(self.bus.locked)
