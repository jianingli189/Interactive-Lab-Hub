#!/usr/bin/env python3
import argparse
import contextlib
import json
import math
import statistics
import sys
import time
from collections import deque
from datetime import datetime, timezone

import board
import motion_capture as hw
from sensor_recovery import RecoveryReader


HZ = 25
PERIOD = 1.0 / HZ
MAX_GAP = 0.12

parser = argparse.ArgumentParser()
parser.add_argument(
    "--step",
    choices=("auto", "chop", "stir", "flip", "twist"),
    default="auto",
)
args = parser.parse_args()

ORIGIN = time.monotonic()
SEQ = 0


def emit(kind, **fields):
    global SEQ
    SEQ += 1
    message = {
        "schema": "kitchen-motion.v1",
        "seq": SEQ,
        "t": round(time.monotonic() - ORIGIN, 3),
        "type": kind,
        **fields,
    }
    print(json.dumps(message, ensure_ascii=True), flush=True)


def norm(values):
    return math.sqrt(sum(x * x for x in values))


def rms(values):
    return math.sqrt(sum(x * x for x in values) / len(values))


class HeadDetector:
    def __init__(self):
        self.cooldown = 0.0
        self.reset()

    def reset(self):
        self.smooth = deque(maxlen=3)
        self.event = []
        self.quiet_since = None
        self.last_t = None

    def update(self, t, values):
        if self.last_t is not None and t - self.last_t > MAX_GAP:
            self.reset()
        self.last_t = t

        self.smooth.append(values[3:6])
        g = tuple(
            sum(v[k] for v in self.smooth) / len(self.smooth)
            for k in range(3)
        )
        strength = norm(g)

        if t < self.cooldown:
            return

        if not self.event:
            if len(self.smooth) == 3 and strength > 0.6:
                self.event = [(t, g)]
            return

        self.event.append((t, g))

        if t - self.event[0][0] > 2.5:
            self.reset()
            self.cooldown = t + 0.3
            return

        if strength < 0.35:
            if self.quiet_since is None:
                self.quiet_since = t
            elif t - self.quiet_since >= 0.16:
                self.finish(t)
        else:
            self.quiet_since = None

    def finish(self, t):
        event = self.event
        self.reset()
        duration = event[-1][0] - event[0][0]
        if not 0.25 <= duration <= 2.5:
            return

        energy = [
            sum(g[k] ** 2 for _, g in event)
            for k in range(3)
        ]
        x_fraction = energy[0] / max(sum(energy), 1e-9)

        x = [g[0] for _, g in event]
        lateral = [
            (g[2] - g[1]) / math.sqrt(2)
            for _, g in event
        ]

        def ordered(a, b, signal):
            first = next(
                (i for i, v in enumerate(signal) if a(v)),
                None,
            )
            return (
                first is not None
                and any(b(v) for v in signal[first + 1:])
            )

        action = None
        if x_fraction > 0.75 and ordered(
            lambda v: v > 2.0,
            lambda v: v < -1.5,
            x,
        ):
            action = "confirm"

        elif x_fraction < 0.25:
            first = next(
                (v for v in lateral if abs(v) > 1.0),
                None,
            )
            if first is not None:
                if first < 0 and ordered(
                    lambda v: v < -1.0,
                    lambda v: v > 0.7,
                    lateral,
                ):
                    action = "next"
                elif first > 0 and ordered(
                    lambda v: v > 1.0,
                    lambda v: v < -0.7,
                    lateral,
                ):
                    action = "undo"

        if action:
            self.cooldown = t + 0.5
            emit(
                "head_event",
                action=action,
                duration=round(duration, 3),
                candidate=True,
            )


def hand_features(rows):
    if len(rows) < 30:
        return None

    # Resample onto a uniform grid using actual RH timestamps.
    # Never interpolate across a missing-data interval.
    if any(
        rows[i][0] - rows[i - 1][0] > MAX_GAP
        for i in range(1, len(rows))
    ):
        return None

    if rows[-1][0] - rows[0][0] < 1.8:
        return None

    grid = []
    index = 0
    t = rows[0][0]

    while t <= rows[-1][0]:
        while (
            index + 1 < len(rows) - 1
            and rows[index + 1][0] < t
        ):
            index += 1

        left, right = rows[index], rows[index + 1]
        fraction = (t - left[0]) / max(right[0] - left[0], 1e-9)
        values = [
            a + fraction * (b - a)
            for a, b in zip(left[1], right[1])
        ]
        grid.append(values)
        t += PERIOD

    energies = [
        sum(v[3 + k] ** 2 for v in grid)
        for k in range(3)
    ]
    total = max(sum(energies), 1e-9)
    dominant = max(range(3), key=lambda k: energies[k])

    signal = [v[3 + dominant] for v in grid]
    mean = statistics.mean(signal)
    signal = [v - mean for v in signal]
    denominator = sum(v * v for v in signal)

    correlation = {}
    if denominator > 1e-9:
        for lag in range(5, min(26, len(signal) // 2)):
            correlation[lag] = sum(
                signal[i] * signal[i + lag]
                for i in range(len(signal) - lag)
            ) / denominator

    # Require a local autocorrelation peak, not merely slow motion.
    peaks = [
        (value, lag)
        for lag, value in correlation.items()
        if lag - 1 in correlation and lag + 1 in correlation
        and value > correlation[lag - 1]
        and value >= correlation[lag + 1]
    ]
    periodicity, lag = max(peaks, default=(0.0, 0))

    return {
        "rh_rms": math.sqrt(total / len(grid)),
        "lh_rms": rms([row[2] for row in rows]),
        "y_fraction": energies[1] / total,
        "acc_sd": statistics.pstdev(
            [norm(v[:3]) for v in grid]
        ),
        "periodicity": max(0.0, periodicity),
        "period_s": lag * PERIOD,
    }


class HandDetector:
    def __init__(self, step):
        self.step = step
        self.strokes = 0
        self.cycles = 0
        self.flips = 0
        self.reset()

    def reset(self):
        # Counts survive faults; incomplete events do not.
        self.rows = deque(maxlen=60)
        self.last_t = None
        self.label = "unknown"
        self.pending_label = None
        self.label_hits = 0
        self.features = None

        self.stroke = []
        self.stroke_sign = 0
        self.stroke_quiet = None
        self.pending_stroke = None

        self.flip = []
        self.flip_quiet = None
        self.flip_blocked = False

    def update(self, t, right, left):
        if self.last_t is not None and t - self.last_t > MAX_GAP:
            self.reset()
        self.last_t = t

        left_strength = norm(left[3:6])
        self.rows.append((t, right, left_strength))
        while self.rows and t - self.rows[0][0] > 2.05:
            self.rows.popleft()

        if self.step in ("auto", "twist"):
            self.update_twist(t, right, left_strength)

        if self.step in ("auto", "flip"):
            self.update_flip(t, right)

    def update_twist(self, t, right, left_strength):
        y = right[4]
        sign = 1 if y > 1.0 else -1 if y < -1.0 else 0

        if self.stroke and sign and sign != self.stroke_sign:
            self.finish_stroke(t)

        if not self.stroke:
            if sign:
                self.stroke_sign = sign
                self.stroke = [(t, right[3:6], left_strength)]
                self.stroke_quiet = None
            return

        self.stroke.append((t, right[3:6], left_strength))

        if t - self.stroke[0][0] > 1.6:
            self.stroke = []
            self.stroke_quiet = None
            return

        if abs(y) < 0.35:
            if self.stroke_quiet is None:
                self.stroke_quiet = t
            elif t - self.stroke_quiet >= 0.12:
                self.finish_stroke(t)
        else:
            self.stroke_quiet = None

    def finish_stroke(self, t):
        event = self.stroke
        sign = self.stroke_sign
        self.stroke = []
        self.stroke_quiet = None

        if len(event) < 3:
            return

        duration = event[-1][0] - event[0][0]
        energy = [
            sum(g[k] ** 2 for _, g, _ in event)
            for k in range(3)
        ]
        y_fraction = energy[1] / max(sum(energy), 1e-9)

        angle = 0.0
        for previous, current in zip(event, event[1:]):
            angle += (
                previous[1][1] + current[1][1]
            ) * 0.5 * (current[0] - previous[0])

        peak = max(abs(g[1]) for _, g, _ in event)
        left_rms = rms([v for _, _, v in event])

        if not (
            0.08 <= duration <= 1.6
            and sign * angle > 0.30
            and peak > 1.5
            and y_fraction > 0.55
            and left_rms > 0.6
        ):
            return

        self.strokes += 1
        emit(
            "hand_event",
            action="twist_stroke",
            candidate=True,
            count=self.strokes,
            direction=sign,
            duration=round(duration, 3),
        )

        previous = self.pending_stroke
        if (
            previous is not None
            and previous[0] != sign
            and 0 < t - previous[1] <= 2.5
        ):
            self.cycles += 1
            self.pending_stroke = None
            emit(
                "hand_event",
                action="twist_cycle",
                candidate=True,
                count=self.cycles,
            )
        else:
            self.pending_stroke = (sign, t)

    def update_flip(self, t, right):
        strength = norm(right[3:6])

        if self.flip_blocked:
            if strength < 0.3:
                if self.flip_quiet is None:
                    self.flip_quiet = t
                elif t - self.flip_quiet >= 0.5:
                    self.flip_blocked = False
                    self.flip_quiet = None
            else:
                self.flip_quiet = None
            return

        if not self.flip:
            if strength > 0.5:
                self.flip = [(t, right[3:6])]
            return

        self.flip.append((t, right[3:6]))
        if t - self.flip[0][0] > 8:
            self.flip = []
            self.flip_blocked = True
            self.flip_quiet = None
            return

        if strength < 0.3:
            if self.flip_quiet is None:
                self.flip_quiet = t
            elif t - self.flip_quiet >= 0.45:
                self.finish_flip()
        else:
            self.flip_quiet = None

    def finish_flip(self):
        event = self.flip
        self.flip = []
        self.flip_quiet = None

        duration = event[-1][0] - event[0][0]
        energy = [
            sum(g[k] ** 2 for _, g in event)
            for k in range(3)
        ]
        y_fraction = energy[1] / max(sum(energy), 1e-9)
        peak = max(norm(g) for _, g in event)

        if (
            0.6 <= duration <= 8
            and y_fraction < 0.25
            and peak > 1.8
        ):
            self.flips += 1
            self.flip_blocked = True
            emit(
                "hand_event",
                action="flip",
                candidate=True,
                count=self.flips,
                duration=round(duration, 3),
            )

    def classify(self):
        f = hand_features(list(self.rows))
        self.features = f
        if f is None:
            self.label = "unknown"
            self.pending_label = None
            self.label_hits = 0
            return

        if f["rh_rms"] < 0.18 and f["lh_rms"] < 0.18:
            label = "idle"
        else:
            label = "unknown"

            if (
                self.step in ("auto", "twist")
                and f["rh_rms"] > 0.8
                and f["lh_rms"] > 0.7
                and f["y_fraction"] > 0.55
            ):
                label = "twist"

            elif (
                self.step in ("auto", "stir")
                and f["rh_rms"] > 1.7
                and f["periodicity"] > 0.45
            ):
                label = "stir"

            elif (
                self.step in ("auto", "chop")
                and 0.35 < f["rh_rms"] < 1.8
                and f["acc_sd"] > 1.0
                and f["periodicity"] > 0.25
                and f["y_fraction"] > 0.45
            ):
                label = "chop"

        if label == self.pending_label:
            self.label_hits += 1
        else:
            self.pending_label = label
            self.label_hits = 1

        # Unknown/idle clear immediately; positive labels need two votes.
        if label in ("unknown", "idle") or self.label_hits >= 2:
            self.label = label


def main():
    i2c = board.I2C()
    head = HeadDetector()
    hands = HandDetector(args.step)

    try:
        # Hardware diagnostics go to stderr.
        # stdout remains JSON only for webpage integration.
        with contextlib.redirect_stdout(sys.stderr):
            devices = hw.initialize(i2c)

        emit(
            "ready",
            step=args.step,
            target_hz=HZ,
            utc=datetime.now(timezone.utc).isoformat(),
            channels=hw.CHANNELS,
        )

        valid = {name: False for name in hw.ORDER}
        errors = {name: "" for name in hw.ORDER}
        last_config = {name: -10.0 for name in hw.ORDER}
        lsm_attempts = {"LH": 0, "HF": 0}
        lsm_retry_at = {"LH": 0.0, "HF": 0.0}

        # RH_BOUNDED_RECOVERY
        rh_recovery_attempts = 0
        rh_recovery_at = 0.0


        start = time.monotonic()
        deadline = start
        report_at = start + 1
        classify_at = start + 0.5
        warmup_until = start + 2

        cycles = 0
        skipped = 0
        io_failures = 0
        interval_max_ms = 0.0
        event_stdout = sys.stdout
        def recovery_event(kind, **fields):
            with contextlib.redirect_stdout(event_stdout):
                emit(kind, **fields)
        recovery = RecoveryReader(hw, recovery_event)

        while True:
            now = time.monotonic()
            if now < deadline:
                time.sleep(deadline - now)

            cycle_start = time.monotonic()
            readings = {}

            # ADAPTIVE_RECOVERY_V1
            for name in hw.ORDER:
                with contextlib.redirect_stdout(sys.stderr):
                    sample = recovery.read(name, devices[name], ORIGIN)
                valid[name] = sample is not None
                if sample is not None:
                    readings[name] = sample
            io_failures = recovery.failures

            now = time.monotonic()

            if "HF" not in readings:
                head.reset()
            elif now >= warmup_until:
                head.update(*readings["HF"])

            if hasattr(hands, "update_available"):
                hands.update_available(readings if now >= warmup_until else {})
            elif "LH" not in readings or "RH" not in readings:
                hands.reset()
            elif now >= warmup_until:
                right_t, right = readings["RH"]
                left_t, left = readings["LH"]

                # Reject pairs too far apart in time.
                if abs(right_t - left_t) <= 0.06:
                    hands.update(right_t, right, left)
                else:
                    hands.reset()

            if now >= classify_at:
                if hasattr(hands, "update_available") or (valid["LH"] and valid["RH"]):
                    hands.classify()
                classify_at = now + 0.5

            cycles += 1
            interval_max_ms = max(
                interval_max_ms,
                (time.monotonic() - cycle_start) * 1000,
            )

            if now >= report_at:
                f = hands.features
                emit(
                    "state",
                    step=args.step,
                    hand_state=hands.label,
                    candidate=True,
                    sensors=valid.copy(),
                    counts={
                        "twist_stroke": hands.strokes,
                        "twist_cycle": hands.cycles,
                        "flip": hands.flips,
                    },
                    features=(
                        {k: round(v, 3) for k, v in f.items()}
                        if f else None
                    ),
                    timing={
                        "loop_hz": round(cycles / (now - start), 2),
                        "skipped_slots": skipped,
                        "max_cycle_ms": round(interval_max_ms, 2),
                        "sensor_read_failures": io_failures,
                        "rh_retries": devices["RH"]["sensor"].retry_count,
                    },
                )
                interval_max_ms = 0.0
                report_at = now + 1

            deadline += PERIOD
            now = time.monotonic()
            if now > deadline:
                missed = int((now - deadline) / PERIOD) + 1
                skipped += missed
                deadline += missed * PERIOD

    finally:
        i2c.deinit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        emit("stopped", reason="user")
    except Exception as exc:
        emit("fatal", message=str(exc))
        sys.exit(1)
