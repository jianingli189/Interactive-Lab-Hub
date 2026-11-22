"""Replay the supplied real head test; no hardware packages required."""
import argparse
import json
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--fast", action="store_true")
args = parser.parse_args()
previous = None
path = Path(__file__).parent / "examples" / "head_session.jsonl"
for line in path.read_text().splitlines():
    event = json.loads(line)
    if previous is not None and not args.fast:
        time.sleep(max(0, event["t"] - previous))
    print(json.dumps(event), flush=True)
    previous = event["t"]
