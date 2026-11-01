"""Phone Sleep Check: Qwiic boundaries, YOLO observations, deterministic report."""
import argparse
import json
import queue
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

MODEL_PATH = str(Path(__file__).with_name('yolo26n_ncnn_model'))
SAMPLE_INTERVAL = 3
CONFIDENCE_THRESHOLD = 0.40
CELL_PHONE_CLASS = 67
NUM_FRAMES = 5
REQUIRED_DETECTIONS = 2
FRAME_DELAY = 0.15
BEDTIME_MESSAGE = ('Your sleep check starts in five seconds. '
                   'I’ll keep an eye on whether your phone stays put tonight. Good night!')


def stamp():
    return {'time': datetime.now().astimezone().isoformat(timespec='milliseconds'),
            'monotonic': time.monotonic()}


class ButtonInput:
    """Poll independently of inference/audio; debounce and enqueue press edges."""
    def __init__(self, device):
        self.device = device
        self.events = queue.Queue()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        try:
            stable = candidate = bool(self.device.is_button_pressed())
            changed = time.monotonic()
            # A button held at launch must be released before it can start a run.
            while not self.stop.wait(0.02):
                value = bool(self.device.is_button_pressed())
                if value != candidate:
                    candidate, changed = value, time.monotonic()
                if candidate != stable and time.monotonic() - changed >= 0.05:
                    stable = candidate
                    if stable:
                        self.events.put(stamp())
        except Exception as error:
            self.events.put(error)

    def poll(self, timeout=0):
        try:
            event = self.events.get(timeout=timeout)
        except queue.Empty:
            return None
        if isinstance(event, Exception):
            raise RuntimeError('Qwiic button read failed') from event
        return event

    def close(self):
        self.stop.set()
        self.thread.join(timeout=1)


class Night:
    def __init__(self):
        self.opened = None
        self.periods = []

    def close_interval(self, at, reason):
        if self.opened is None:
            return None
        period = {'start': self.opened['time'], 'end': at['time'],
                  'duration_seconds': round(at['monotonic'] - self.opened['monotonic'], 3),
                  'end_reason': reason}
        self.periods.append(period)
        self.opened = None
        return period

    def observe(self, present, at):
        if present is None:
            return 'observation_unknown', None
        if not present and self.opened is None:
            self.opened = at
            return 'phone_missing', None
        if present and self.opened is not None:
            return 'phone_returned', self.close_interval(at, 'phone_returned')
        return 'observation', None


def report(check_in, ended, periods):
    text = f"Good morning! You checked in your phone at {check_in}. "
    if not periods:
        text += 'I did not notice any possible phone use during your sleep check. '
    else:
        text += f'I noticed {len(periods)} possible phone-use periods. '
        for p in periods:
            text += (f"From {p['start']} to {p['end']}, "
                     f"about {p['duration_seconds']:.1f} seconds. ")
            if p['end_reason'] == 'morning_button':
                text += 'The phone was still missing when you ended monitoring. '
    return text + f'You ended the sleep check at {ended}. These are sampled observations, not proof of phone activity.'


def speak(text):
    # Preserve speech text while tolerating legacy terminal encodings.
    encoding = getattr(sys.stdout, 'encoding', None) or 'utf-8'
    display_text = text.encode(encoding, errors='backslashreplace').decode(encoding)
    print('\nSPEAKER:', display_text, flush=True)
    subprocess.run(['espeak', '-b', '1', '-s', '145', '--stdin'],
                   input=text.encode('utf-8'), check=True)


def detect_phone(cap, model, interrupt):
    count, valid, confidence = 0, 0, None
    for _ in range(NUM_FRAMES):
        interrupt()
        ok, frame = cap.read()
        if ok:
            valid += 1
            results = model(frame, imgsz=320, conf=CONFIDENCE_THRESHOLD,
                            classes=[CELL_PHONE_CLASS], verbose=False)
            scores = [float(box.conf.item()) for result in results for box in result.boxes]
            if scores:
                count += 1
                confidence = max(scores + ([confidence] if confidence is not None else []))
        interrupt()
        time.sleep(FRAME_DELAY)
    print(f'Phone vote: {count}/{NUM_FRAMES}; valid frames: {valid}', flush=True)
    # Camera failure must not be interpreted as phone absence.
    return (count >= REQUIRED_DETECTIONS if valid == NUM_FRAMES else None), {
        'detections': count, 'valid_frames': valid, 'confidence': confidence}


class EndSession(Exception):
    def __init__(self, at):
        self.at = at


def main():
    # Logs/reports may contain Unicode even over a Latin-1 SSH terminal.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='backslashreplace')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--button-address', type=lambda s: int(s, 0), default=0x6F)
    parser.add_argument('--log', default='night_log.jsonl')
    parser.add_argument('--run-kind', choices=['compressed_demo', 'real_night'], default='compressed_demo')
    args = parser.parse_args()
    import cv2
    import qwiic_button
    from ultralytics import YOLO

    run_id = str(uuid.uuid4())
    def log(event, at=None, **data):
        row = dict(at or stamp(), event=event, run_id=run_id, run_kind=args.run_kind, **data)
        with open(args.log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
        print(row, flush=True)

    device = qwiic_button.QwiicButton(args.button_address)
    if not device.begin():
        raise RuntimeError(f'Qwiic button not found at {args.button_address:#04x}. Check I2C and the configured address.')
    print(f'Qwiic button ready at {args.button_address:#04x}')
    cap = None
    button = None
    night = Night()
    monitoring = False
    try:
        model = YOLO(MODEL_PATH)
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not cap.isOpened():
            raise RuntimeError('Could not open camera')
        button = ButtonInput(device)
        print('Press and release the Qwiic button when ready for bed.')
        first = None
        while first is None:
            first = button.poll(0.1)
        log('bedtime_button', first)
        print('Place your phone in the Phone Bed. Waiting for stable detection.')

        def interrupt():
            event = button.poll()
            if event is not None:
                raise EndSession(event)

        while True:
            present, details = detect_phone(cap, model, interrupt)
            if present:
                check_in = stamp()
                log('phone_checked_in', check_in, **details)
                break
            time.sleep(0.1)
        speak(BEDTIME_MESSAGE)
        interrupt()
        deadline = time.monotonic() + 5
        print('Grace period: 5 seconds...')
        while time.monotonic() < deadline:
            interrupt()
            time.sleep(0.02)
        log('monitoring_started')
        monitoring = True
        while True:
            present, details = detect_phone(cap, model, interrupt)
            at = stamp()
            interrupt()
            event, period = night.observe(present, at)
            log(event, at, phone_detected=present, interval=period, **details)
            deadline = time.monotonic() + SAMPLE_INTERVAL
            while time.monotonic() < deadline:
                interrupt()
                time.sleep(0.02)
    except EndSession as end:
        if not monitoring:
            log('session_cancelled', end.at, reason='second_button_before_monitoring')
            print('Cancelled before monitoring; press again after restarting the program.')
        else:
            log('morning_button', end.at)
            night.close_interval(end.at, 'morning_button')
            log('monitoring_ended', end.at, possible_phone_use_periods=night.periods,
                total_possible_use_seconds=round(sum(p['duration_seconds'] for p in night.periods), 3))
            text = report(check_in['time'], end.at['time'], night.periods)
            log('morning_report', report=text)
            speak(text)
    except (KeyboardInterrupt, Exception) as error:
        at = stamp()
        night.close_interval(at, 'aborted')
        log('session_aborted', at, reason=type(error).__name__, error=str(error),
            possible_phone_use_periods=night.periods)
        if not isinstance(error, KeyboardInterrupt):
            raise
    finally:
        if button is not None:
            button.close()
        if cap is not None:
            cap.release()
        print(f'Log saved to {args.log}')


if __name__ == '__main__':
    main()
