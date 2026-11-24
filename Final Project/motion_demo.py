#!/usr/bin/env python3
"""Demonstration only: generic movement, never claims an action class.
Uses motion_live.py for hardware acquisition, fault handling and head gestures.
The web reducer requires the current action's tool pickup (sensor or manual).
"""
from collections import deque
import math
import statistics
import runpy
import sys
import traceback
from pathlib import Path

program = runpy.run_path(str(Path(__file__).with_name("motion_live.py")), run_name="motion_demo_source")
g = program["main"].__globals__
original_emit = g["emit"]
def demo_emit(kind, **fields):
    fields["recognition_mode"] = "demo"
    original_emit(kind, **fields)
g["emit"] = demo_emit
Base = g["HandDetector"]
class DemoHands(Base):
    def update_twist(self, *args):
        pass
    def update_flip(self, *args):
        pass
    def update_available(self, readings):
        available = tuple(n for n in ('LH', 'RH') if n in readings)
        if available != getattr(self, 'available', None):
            self.reset()
            self.available = available
            self.windows = {n: deque(maxlen=60) for n in available}
        for n in available:
            t, values = readings[n]
            rows = self.windows[n]
            if rows and t - rows[-1][0] > 0.12:
                rows.clear()
                self.label = 'unknown'
                self.label_hits = 0
                self.pending_label = None
            rows.append((t, values))
            while rows and t - rows[0][0] > 2.05:
                rows.popleft()

    def classify(self):
        features = {}
        for n, rows in getattr(self, 'windows', {}).items():
            if len(rows) < 20 or rows[-1][0] - rows[0][0] < 0.8:
                continue
            gyro = math.sqrt(sum(sum(v*v for v in values[3:6]) for _, values in rows)/len(rows))
            acc = statistics.pstdev(math.sqrt(sum(v*v for v in values[:3])) for _, values in rows)
            features[n + '_gyro_rms'] = gyro
            features[n + '_acc_sd'] = acc
        self.features = features or None
        if not features:
            self.label = 'unknown'
            self.label_hits = 0
            self.pending_label = None
            return
        # Demo only; these broad thresholds are not an action classifier.
        moving = any(v > (0.35 if k.endswith('gyro_rms') else 0.5) for k,v in features.items())
        wanted = 'moving' if moving else 'idle'
        self.label_hits = self.label_hits + 1 if wanted == self.pending_label else 1
        self.pending_label = wanted
        if not moving or self.label_hits >= 2:
            self.label = wanted
g["HandDetector"] = DemoHands
if __name__ == "__main__":
    try:
        g["main"]()
    except KeyboardInterrupt:
        demo_emit("stopped", reason="user")
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        demo_emit("fatal", message=str(exc))
        sys.exit(1)
