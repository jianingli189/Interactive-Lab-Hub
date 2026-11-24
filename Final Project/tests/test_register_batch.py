import ast
import unittest
from pathlib import Path

class BatchTests(unittest.TestCase):
    def test_group_uses_single_lock_and_preserves_order(self):
        source=(Path(__file__).parents[1]/'motion_capture.py').read_text()
        tree=ast.parse(source)
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('read_regs','read_reg')]
        events=[]
        class Device:
            def __init__(self,*args,**kwargs): pass
            def __enter__(self): events.append('enter');return self
            def __exit__(self,*args): events.append('exit')
            def write_then_readinto(self,reg,result):
                events.append(reg[0]);result[0]=reg[0]+1
        env={'I2CDevice':Device}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'batch','exec'),env)
        self.assertEqual(env['read_regs'](None,0x28,(7,0,0x3d)),(8,1,0x3e))
        self.assertEqual(events,['enter',7,0,0x3d,'exit'])
