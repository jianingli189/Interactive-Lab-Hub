"""Offline publisher-format to MQTT callback to SSE verification; no broker contact."""
import ast
import json
import queue
import sys
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bridge'))
from sensor_bridge import Hub
from utensil_mqtt import start_mqtt
class Client:
    def __init__(self,*a,**k): self.subscriptions=[]
    def username_pw_set(self,*a): pass
    def reconnect_delay_set(self,*a): pass
    def max_queued_messages_set(self,*a): pass
    def connect_async(self,*a,**k): pass
    def loop_start(self): pass
    def subscribe(self,*a,**k): self.subscriptions.append(a[0])
class ChainTests(unittest.TestCase):
    def test_publisher_callback_sse(self):
        tree=ast.parse((ROOT/'pi-utensils/utensil_detection.py').read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='publish_states')
        config=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONFIG' for t in n.targets))
        config=ast.literal_eval(config)
        sent=[]
        g={'CONFIG':config,'time':time,'sensor_valid':{c:True for c in config},'last_success':{},'MQTT_STATE_TOPIC':'IDD/jianing-kitchen/utensil/state','publish_message':lambda t,p,**kw:sent.append((t,p))}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'publisher','exec'),g)
        mqtt=types.ModuleType('paho.mqtt.client');mqtt.Client=Client;mqtt.CallbackAPIVersion=types.SimpleNamespace(VERSION2=2)
        parent=types.ModuleType('paho');sub=types.ModuleType('paho.mqtt');parent.mqtt=sub;sub.client=mqtt
        hub=Hub('live');q=queue.Queue();hub.add(q)
        with patch.dict(sys.modules,{'paho':parent,'paho.mqtt':sub,'paho.mqtt.client':mqtt}),patch.dict('os.environ',{'KITCHEN_MQTT_PASSWORD':'test-only'}):
            client=start_mqtt(hub,'offline.test','IDD/jianing-kitchen/utensil')
            client.on_connect(client,None,None,types.SimpleNamespace(is_failure=False),None)
            self.assertEqual(client.subscriptions,['IDD/jianing-kitchen/utensil/state'])
            for present in (True,False,True):
                g['publish_states']({c:present for c in config})
                client.on_message(client,None,types.SimpleNamespace(retain=False,payload=json.dumps(sent[-1][1]).encode()))
                for item in hub.utensils['utensils'].values():
                    self.assertEqual(item['present'],present);self.assertTrue(item['valid']);self.assertTrue(item['healthKnown'])
            g['sensor_valid'][1]=False;g['publish_states']({c:True for c in config})
            client.on_message(client,None,types.SimpleNamespace(retain=False,payload=json.dumps(sent[-1][1]).encode()))
            self.assertIsNone(hub.utensils['utensils']['knife']['present'])
            stream=b''.join(list(q.queue)).decode();self.assertIn('event: utensil\n',stream)
            client.on_disconnect(client,None,None,None,None)
            self.assertFalse(hub.mqtt_connected);self.assertIsNone(hub.utensils)
