#!/usr/bin/env python3
"""
sensor_bridge.py - Raspberry Pi motion_live.py -> browser, via Server-Sent Events.

Standard library only (no pip install). Runs ONE motion_live.py process no
matter how many browsers connect (only one process may own the I2C bus), reads
its stdout line by line (each line is one kitchen-motion.v1 JSON object), and
forwards every valid message to all connected pages as

    event: motion
    data: {"sessionId": "...", "receivedAt": <ms>, "event": {...the original JSON...}}

stderr from motion_live.py (hardware diagnostics) is passed through to this
process's stderr and is never mixed into the data stream.

On each browser (re)connection the bridge first sends

    event: hello
    data: {"sessionId", "lastSeq", "bridgeNow", "processRunning", "source", "ready", "latestState"}

and NO backlog of head/hand events, so stale gestures can never replay.
When motion_live.py exits, an `event: bridge` status is sent and the process is
restarted after --restart-delay seconds with a new sessionId (seq restarts at 1).

Usage on the Pi (from anywhere):
    python3 sensor_bridge.py --motion-dir "/home/pi/Interactive-Lab-Hub/Final Project"
Without hardware (replays a recorded JSONL log with its original timing):
    python3 sensor_bridge.py --replay fixtures/mixed_session_20261121.jsonl --loop
Then open the website with  ?sensors=http://<pi-host>:8765
"""
import argparse
import json
import os
import queue
import signal
import shlex
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCHEMA = "kitchen-motion.v1"


def log(*parts):
    print("[bridge]", *parts, file=sys.stderr, flush=True)


def now_ms():
    return int(time.time() * 1000)


class Hub:
    """Latest state + connected clients. Thread-safe."""

    def __init__(self, source):
        self.lock = threading.Lock()
        self.clients = set()
        self.source = source
        self.session_id = None
        self.last_seq = 0
        self.ready = None
        self.latest_state = None
        self.running = False
        self.invalid_lines = 0
        self.utensils = None
        self.mqtt_connected = False

    def new_session(self):
        with self.lock:
            self.session_id = str(uuid.uuid4())
            self.last_seq = 0
            self.ready = None
            self.latest_state = None
            self.running = True
            sid = self.session_id
        self.broadcast("bridge", {"status": "started", "sessionId": sid, "bridgeNow": now_ms()})
        return sid

    def ended(self, status, code=None):
        with self.lock:
            self.running = False
            sid = self.session_id
        self.broadcast("bridge", {"status": status, "sessionId": sid, "code": code, "bridgeNow": now_ms()})

    def hello(self):
        with self.lock:
            return {
                "sessionId": self.session_id,
                "lastSeq": self.last_seq,
                "bridgeNow": now_ms(),
                "processRunning": self.running,
                "source": self.source,
                "ready": self.ready,
                "latestState": self.latest_state,
                "utensils": self.utensils,
                "mqttConnected": self.mqtt_connected,
            }

    def add(self, q):
        with self.lock:
            self.clients.add(q)

    def remove(self, q):
        with self.lock:
            self.clients.discard(q)

    def broadcast(self, event, data):
        # CONSOLE_INPUT_STATUS_V2: readable stdout; detailed diagnostics stay on stderr.
        def say(label, text):
            print(time.strftime("%H:%M:%S"), "[" + label + "]", text, flush=True)
        now = time.monotonic()
        if event == "motion":
            e = data.get("event", {})
            kind = e.get("type")
            if kind == "state":
                hand = e.get("hand_state", "unknown")
                bad = [k for k, v in e.get("sensors", {}).items() if v is not True]
                key = (hand, tuple(bad))
                if key != getattr(self, "_console_state", None) or now - getattr(self, "_console_at", 0) >= 2:
                    self._console_state, self._console_at = key, now
                    names = {"idle":"静止", "unknown":"暂未识别", "stir":"搅拌", "chop":"切菜", "twist":"拧瓶", "moving":"明显运动（展示版，结合网页步骤）"}
                    usable = [n for n in ('LH', 'RH') if e.get('sensors', {}).get(n) is True]
                    demo = e.get('recognition_mode') == 'demo'
                    text = names.get(hand, hand)
                    if not usable or (not demo and len(usable) < 2):
                        text = '传感器异常，暂停判断'
                    elif demo and len(usable) == 1:
                        text += '（仅左手有效）' if usable[0] == 'LH' else '（仅右手有效）'
                    say('手部状态', text)
                    if bad: say("传感器异常", ", ".join(bad))
            elif kind == "head_event":
                action = e.get("action", "")
                say("头部动作", {"confirm":"向前点头：完成", "next":"向右点头：下一步", "undo":"向左点头：撤销"}.get(action, action))
            elif kind == "hand_event":
                action = e.get("action", "")
                name = {"twist_stroke":"单向拧转候选", "twist_cycle":"往返拧转候选", "flip":"翻面候选"}.get(action, action)
                say("手部事件", name + "，累计 " + str(e.get("count", "?")))
            elif kind == "ready": say("设备", "初始化完成，开始读取头部和手部")
            elif kind == "recovery_attempt": say("设备", str(e.get("sensor", "RH")) + " 自动恢复，第 " + str(e.get("attempt")) + " 次")
            elif kind == "recovery_configured": say("设备", str(e.get("sensor", "RH")) + " 配置已恢复，等待有效数据")
            elif kind == "sensor_recovered": say("设备", str(e.get("sensor")) + " 已重新读到有效数据")
            elif kind in ("fatal", "sensor_fault", "recovery_failed", "recovery_exhausted"):
                say("设备异常", str(e.get("sensor", "")) + " " + str(e.get("message", kind)))
            elif kind == "stopped": say("设备", "动作程序已停止")
        elif event == "utensil":
            names = {"knife":"刀", "chopsticks":"筷子", "spatula":"铲子", "salt_shaker":"盐瓶", "pepper_grinder":"黑胡椒瓶"}
            values = data.get("utensils", {})
            before = getattr(self, "_console_tools", {})
            for name, item in values.items():
                if before.get(name) == item: continue
                text = "读数无效" if not item.get("valid") or item.get("present") is None else ("在摆放位置" if item["present"] else "离开摆放位置")
                if not item.get("healthKnown"): text += "（旧版消息，未提供有效状态）"
                say("厨具", names.get(name, name) + "：" + text)
            self._console_tools = {k: dict(v) for k, v in values.items()}
        elif event == "utensil_link":
            self._console_tools = {}
            say("MQTT", "已连接服务器，等待厨具消息" if data.get("connected") else "连接断开")
        elif event == "bridge":
            self._console_state = None
            say("程序", "正在启动动作识别" if data.get("status") == "started" else "动作程序退出，退出码 " + str(data.get("code")))
        payload = f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'))}\n\n".encode()
        with self.lock:
            clients = list(self.clients)
        for q in clients:
            try:
                q.put_nowait(payload)
            except queue.Full:
                # a stalled client must not hold back the others; it will reconnect and get a fresh hello
                self.remove(q)
                while not q.empty():
                    try: q.get_nowait()
                    except queue.Empty: break
                q.put_nowait(None)

    def line(self, raw):
        """Handle one stdout line from motion_live.py (or a replay file)."""
        raw = raw.strip()
        if not raw:
            return
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            self.invalid_lines += 1
            log("invalid JSON line ignored:", exc.msg, raw[:120])
            return
        if not isinstance(event, dict) or event.get("schema") != SCHEMA or not isinstance(event.get("seq"), int):
            self.invalid_lines += 1
            log("non kitchen-motion.v1 line ignored:", raw[:120])
            return
        with self.lock:
            sid = self.session_id
            self.last_seq = max(self.last_seq, event["seq"])
            if event.get("type") == "ready":
                self.ready = event
            elif event.get("type") == "state":
                self.latest_state = event
        self.broadcast("motion", {"sessionId": sid, "receivedAt": now_ms(), "event": event})


def run_live(hub, args, stop):
    motion_dir = Path(args.motion_dir or "/home/pi/Interactive-Lab-Hub/Final Project").expanduser()
    if not args.ssh:
        motion_dir = motion_dir.resolve()
    script_name = "motion_demo.py" if args.demo else "motion_live.py"
    script = motion_dir / script_name
    if not args.ssh and not script.exists():
        log(f"motion_live.py not found in {motion_dir}")
        sys.exit(2)
    python = args.python
    if not python:
        venv = motion_dir / ".venv" / "bin" / "python"
        python = str(venv) if args.ssh or venv.exists() else sys.executable
    launches = 0
    while not stop.is_set():
        if launches >= 4:
            log("Automatic restart limit reached. Inspect devices before manual restart.")
            print("自动重启达到上限，请检查设备后手动重启。", flush=True)
            hub.ended("exited", None)
            return
        launches += 1
        sid = hub.new_session()
        log(f"starting {script_name} (session {sid[:8]}) with {python}")
        command = [python, "-u", script_name, "--step", args.step]
        if args.ssh:
            remote = "cd " + shlex.quote(str(motion_dir)) + " && exec " + shlex.join(command)
            command = ["ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
                       "-o", "ServerAliveInterval=5", "-o", "ServerAliveCountMax=2", args.ssh, remote]
        child = subprocess.Popen(
            command,
            cwd=None if args.ssh else str(motion_dir),
            stdout=subprocess.PIPE,
            stderr=None,  # diagnostics pass straight through to our stderr
            text=True,
            bufsize=1,
        )
        hub.child = child
        # Separate supervisor can stop a reader blocked inside I2C/lock acquisition.
        monitor_done = threading.Event()
        progress = [time.monotonic()]
        def watch_reader(process=child):
            while not monitor_done.wait(1):
                if stop.is_set() or process.poll() is not None:
                    return
                if time.monotonic() - progress[0] > 20:
                    print(time.strftime("%H:%M:%S"), "[设备异常] 动作程序超过20秒没有输出，正在停止并尝试重启", flush=True)
                    hub.ended("restarting", None)
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            print("动作进程无法退出；不会启动第二个读取进程。请关闭系统并检查总线。", flush=True)
                    return
        monitor = threading.Thread(target=watch_reader, daemon=True)
        monitor.start()
        try:
            for raw in child.stdout:
                progress[0] = time.monotonic()
                hub.line(raw)
        finally:
            monitor_done.set()
            monitor.join(timeout=7)
        code = child.wait()
        log(f"motion_live.py exited with code {code}")
        if stop.is_set():
            hub.ended("exited", code)
            break
        hub.ended("restarting", code)
        stop.wait(args.restart_delay)


def run_replay(hub, args, stop):
    path = Path(args.replay)
    lines = [l for l in path.read_text().splitlines() if l.strip()]
    while not stop.is_set():
        hub.new_session()
        log(f"replaying {len(lines)} lines from {path.name}")
        previous = None
        for raw in lines:
            if stop.is_set():
                return
            try:
                t = json.loads(raw).get("t")
            except (json.JSONDecodeError, AttributeError):
                t = None
            if previous is not None and isinstance(t, (int, float)):
                stop.wait(0.05 if args.fast else max(0.0, t - previous))
            if isinstance(t, (int, float)):
                previous = t
            hub.line(raw)
        if not args.loop:
            hub.ended("replay-finished")
            return
        stop.wait(2)


def make_handler(hub, allow_origin):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *a):  # keep stderr for real diagnostics
            pass

        def handle(self):
            try:
                super().handle()
            except (ConnectionResetError, BrokenPipeError):
                pass  # browser closed the tab / reconnected; nothing to report

        def cors(self):
            self.send_header("Access-Control-Allow-Origin", allow_origin)
            self.send_header("Cache-Control", "no-cache")

        def do_GET(self):
            if self.path.startswith("/health"):
                body = json.dumps({**hub.hello(), "clients": len(hub.clients), "invalidLines": hub.invalid_lines}).encode()
                self.send_response(200)
                self.cors()
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if not self.path.startswith("/events"):
                self.send_error(404)
                return
            self.send_response(200)
            self.cors()
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q = queue.Queue(maxsize=500)
            hub.add(q)
            try:
                hello = json.dumps(hub.hello(), separators=(",", ":"))
                self.wfile.write(f"retry: 1500\nevent: hello\ndata: {hello}\n\n".encode())
                self.wfile.flush()
                while True:
                    try:
                        chunk = q.get(timeout=10)
                    except queue.Empty:
                        chunk = b": keep-alive\n\n"
                    if chunk is None:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                hub.remove(q)

    return Handler


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--motion-dir", help="folder containing motion_live.py and motion_capture.py")
    src.add_argument("--ssh", help="Run motion on Pi over key-authenticated SSH, e.g. pi@hostname")
    src.add_argument("--replay", help="replay a recorded kitchen-motion.v1 JSONL file instead of hardware")
    p.add_argument("--remote-dir", default="/home/pi/Interactive-Lab-Hub/Final Project")
    p.add_argument("--demo", action="store_true", help="Use generic movement demonstration, not action classification")
    p.add_argument("--mqtt", action="store_true", help="Subscribe to utensil MQTT")
    p.add_argument("--mqtt-host", default="farlab.infosci.cornell.edu")
    p.add_argument("--mqtt-prefix", default="IDD/jianing-kitchen/utensil")
    p.add_argument("--python", help="python executable for motion_live.py (default: <motion-dir>/.venv/bin/python)")
    p.add_argument("--step", default="auto", choices=["auto", "chop", "stir", "flip", "twist"])
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--allow-origin", default="*", help="CORS origin of the website")
    p.add_argument("--restart-delay", type=float, default=3.0)
    p.add_argument("--fast", action="store_true", help="replay: ignore original timing")
    p.add_argument("--loop", action="store_true", help="replay: start again at the end")
    args = p.parse_args()
    if args.ssh:
        args.motion_dir = args.remote_dir

    hub = Hub("replay" if args.replay else "live")
    hub.child = None
    stop = threading.Event()
    def supervise():
        try:
            (run_replay if args.replay else run_live)(hub, args, stop)
        except Exception as exc:
            log("source failed:", str(exc))
            hub.ended("exited", 1)
    worker = threading.Thread(target=supervise, daemon=True)

    server = ThreadingHTTPServer((args.host, args.port), make_handler(hub, args.allow_origin))
    server.daemon_threads = True

    def shutdown(*_):
        stop.set()
        child = getattr(hub, "child", None)
        if child and child.poll() is None:
            child.send_signal(signal.SIGINT)  # lets motion_live.py emit "stopped" and release I2C
            try:
                child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                child.kill()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    mqtt_client = None
    if args.mqtt:
        from utensil_mqtt import start_mqtt
        mqtt_client = start_mqtt(hub, args.mqtt_host, args.mqtt_prefix)
    worker.start()
    log(f"listening on http://{args.host}:{args.port}/events  (health: /health)")
    try:
        server.serve_forever()
    finally:
        stop.set()
        if mqtt_client:
            mqtt_client.disconnect()
            mqtt_client.loop_stop()
        server.server_close()


if __name__ == "__main__":
    main()
