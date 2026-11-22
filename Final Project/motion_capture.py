#!/usr/bin/env python3
import argparse
import math
import time

import board
import adafruit_bno055
import adafruit_msa3xx
import adafruit_tca9548a
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_lsm6ds import AccelRange, GyroRange, Rate
from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC


class OriginalLSM6DS3(LSM6DS3TRC):
    CHIP_ID = 0x69


# task: (printed sensors, action duration, instruction)
TASKS = {
    "idle": (
        ("LH", "HF", "HS", "RH"), 6,
        "Stand naturally. Keep head and hands still."
    ),
    "head_forward": (
        ("HF", "HS"), 6,
        "ONE forward nod, then return to neutral and hold."
    ),
    "head_right": (
        ("HF", "HS"), 6,
        "ONE intended right gesture, return to neutral and hold."
    ),
    "head_left": (
        ("HF", "HS"), 6,
        "ONE intended left gesture, return to neutral and hold."
    ),
    "head_other": (
        ("HF", "HS"), 8,
        "Natural head movements only. NO command gestures."
    ),
    "chop": (
        ("LH", "RH"), 8,
        "Chop repeatedly at one consistent, comfortable speed."
    ),
    "stir": (
        ("LH", "RH"), 8,
        "Stir continuously with the tool specified in your note."
    ),
    "flip": (
        ("LH", "RH"), 6,
        "ONE complete spatula flip, then hold. Slow is allowed."
    ),
    "twist": (
        ("LH", "RH"), 8,
        "ONE dispensing twist at each TWIST cue. Three in total."
    ),
    "hands_other": (
        ("LH", "RH"), 8,
        "Pick up/put down tools or move bowl. No target actions."
    ),
    "combined": (
        ("LH", "HF", "HS", "RH"), 8,
        "Perform the combined activity specified in your note."
    ),
}

ORDER = ("LH", "HF", "HS", "RH")
CHANNELS = {"LH": 0, "HF": 3, "HS": 5, "RH": 4}


def scan(bus):
    limit = time.monotonic() + 3
    while not bus.try_lock():
        if time.monotonic() > limit:
            raise TimeoutError("I2C lock timeout")
        time.sleep(0.001)
    try:
        return bus.scan()
    finally:
        bus.unlock()


def read_reg(bus, address, register):
    result = bytearray(1)
    with I2CDevice(bus, address, probe=False) as device:
        device.write_then_readinto(bytes([register]), result)
    return result[0]


def configuration(item):
    bus, address = item["bus"], item["address"]
    if item["name"] == "HS":
        sensor = item["sensor"]
        return (sensor.range, sensor.data_rate, sensor.power_mode)
    if item["name"] == "RH":
        page = read_reg(bus, address, 0x07)
        identity = read_reg(bus, address, 0x00)
        mode = read_reg(bus, address, 0x3D)
        status = read_reg(bus, address, 0x39)
        if (page, identity, mode, status) != (0, 0xA0, 8, 5):
            error = read_reg(bus, address, 0x3A)
            raise RuntimeError(
                f"RH bad state: page={page}, id={identity}, "
                f"mode={mode}, status={status}, sys_err={error}"
            )
        units = read_reg(bus, address, 0x3B)
        power = read_reg(bus, address, 0x3E)
        if units != 0 or power != 0:
            raise RuntimeError(
                f"RH units/power changed: units={units:02X} power={power:02X}"
            )
        return (identity, mode)
    return tuple(
        read_reg(bus, address, r) for r in (0x0F, 0x10, 0x11, 0x12)
    )



class DirectBNO055:
    """One accel/gyro burst per sample, with bounded read retries."""

    def __init__(self, bus, address=0x28):
        self.device = I2CDevice(bus, address, probe=False)
        self.retry_count = 0
        self.recovered_reads = 0

    def read_sample(self):
        import struct

        # 0x08..0x19:
        # accel: bytes 0..5; mag: 6..11; gyro: 12..17.
        # Units are explicitly configured and checked elsewhere.
        for attempt in range(3):
            result = bytearray(18)
            try:
                with self.device as dev:
                    started = time.monotonic()
                    dev.write_then_readinto(b"\x08", result)
                    finished = time.monotonic()

            except OSError as exc:
                if exc.errno != 121 or attempt == 2:
                    print(
                        f"# RH_READ_FAILED attempt={attempt + 1} "
                        f"error={exc!r}",
                        flush=True,
                    )
                    raise

                self.retry_count += 1
                print(
                    f"# RH_RETRY retry={attempt + 1}/2 "
                    f"total={self.retry_count} errno=121",
                    flush=True,
                )
                # Bus lock has been released before waiting.
                time.sleep(0.005 * (attempt + 1))
                continue

            if attempt:
                self.recovered_reads += 1
                print(
                    f"# RH_READ_RECOVERED attempts={attempt + 1}",
                    flush=True,
                )

            ax, ay, az, _, _, _, gx, gy, gz = struct.unpack(
                "<9h", result
            )
            gyro_scale = math.pi / (180.0 * 16.0)
            values = (
                ax * 0.01, ay * 0.01, az * 0.01,
                gx * gyro_scale, gy * gyro_scale, gz * gyro_scale,
            )
            return (started + finished) / 2, values


def rh_state(item):
    regs = (0x07, 0x00, 0x3D, 0x39, 0x3A, 0x3B, 0x3E)
    return tuple(
        read_reg(item["bus"], item["address"], reg)
        for reg in regs
    )


def rh_report(item, label):
    try:
        state = rh_state(item)
        fields = ("PAGE", "ID", "MODE", "STATUS", "ERR", "UNITS", "POWER")
        print(
            "# RH_STATE " + label + " " +
            " ".join(f"{k}={v:02X}" for k, v in zip(fields, state)),
            flush=True,
        )
        return state
    except Exception as exc:
        print(f"# RH_STATE {label} READ_ERROR={exc!r}", flush=True)
        return None


def rh_ready(state):
    if state is None:
        return False
    page, identity, mode, status, error, units, power = state
    return (
        page == 0 and identity == 0xA0
        and mode == 0x08 and status == 0x05
        and units == 0 and power == 0
    )


def rh_configure(item):
    dev = item["sensor"].device

    def write(reg, value, delay=0.05):
        print(
            f"# RH_WRITE reg={reg:02X} value={value:02X}",
            flush=True,
        )
        with dev:
            dev.write(bytes((reg, value)))
        time.sleep(delay)
        actual = read_reg(item["bus"], item["address"], reg)
        if actual != value:
            raise RuntimeError(
                f"RH write failed reg={reg:02X} "
                f"expected={value:02X} actual={actual:02X}"
            )

    rh_report(item, "BEFORE_CONFIG")
    write(0x07, 0x00)
    write(0x3D, 0x00, 0.10)
    write(0x3E, 0x00)
    write(0x3B, 0x00)
    write(0x3D, 0x08, 0.10)

    deadline = time.monotonic() + 3.0
    consecutive = 0
    while time.monotonic() < deadline:
        state = rh_state(item)
        consecutive = consecutive + 1 if rh_ready(state) else 0
        if consecutive >= 3:
            rh_report(item, "CONFIG_READY")
            return
        time.sleep(0.10)

    rh_report(item, "CONFIG_FAILED")
    raise RuntimeError("RH did not reach stable IMUPLUS mode")


def prepare_trial(devices):
    item = devices["RH"]
    state = rh_report(item, "BEFORE_TRIAL")

    if not rh_ready(state):
        print("# RH_RECOVERY one configuration attempt", flush=True)
        rh_configure(item)

    # Confirm actual data, not just a successful mode write.
    origin = time.monotonic()
    for _ in range(10):
        check_configuration(devices)
        for name in ORDER:
            read_one(devices[name], origin)
        time.sleep(0.05)

    print("# PREFLIGHT_OK all four sensors ready", flush=True)


def initialize(i2c):
    mux = adafruit_tca9548a.TCA9548A(i2c, address=0x70)
    devices = {}

    for name in ORDER:
        channel = CHANNELS[name]
        bus = mux[channel]
        found = scan(bus)
        choices = (
            (0x62,) if name == "HS"
            else (0x28, 0x29) if name == "RH"
            else (0x6A, 0x6B)
        )
        matches = [a for a in choices if a in found]
        if len(matches) != 1:
            raise RuntimeError(
                f"{name} CH{channel}: expected one sensor; "
                f"scan={[hex(a) for a in found]}"
            )
        address = matches[0]

        if name == "HS":
            sensor = adafruit_msa3xx.MSA311(bus)
            sensor.range = adafruit_msa3xx.Range.RANGE_4_G
            sensor.data_rate = adafruit_msa3xx.DataRate.RATE_125_HZ
            sensor.power_mode = adafruit_msa3xx.Mode.NORMAL
            model = "MSA311_ACCEL_ONLY"
            time.sleep(0.1)
        elif name == "RH":
            sensor = DirectBNO055(bus, address=address)
            model = "BNO055"
            rh_configure({
                "name": name, "bus": bus,
                "address": address, "sensor": sensor,
            })
        else:
            identity = read_reg(bus, address, 0x0F)
            if identity == 0x6A:
                sensor = LSM6DS3TRC(bus, address=address)
                model = "LSM6DS3TRC"
            elif identity == 0x69:
                sensor = OriginalLSM6DS3(bus, address=address)
                model = "LSM6DS3"
            else:
                raise RuntimeError(
                    f"{name}: unsupported chip ID {identity:02X}"
                )
            sensor.accelerometer_range = AccelRange.RANGE_4G
            sensor.gyro_range = GyroRange.RANGE_2000_DPS
            sensor.accelerometer_data_rate = Rate.RATE_104_HZ
            sensor.gyro_data_rate = Rate.RATE_104_HZ

        item = {
            "name": name, "bus": bus, "address": address,
            "sensor": sensor,
        }
        item["baseline"] = configuration(item)

        if name == "RH":
            expected = (0xA0, 0x08)
        elif name in ("LH", "HF"):
            expected = (identity, 0x48, 0x4C, 0x44)
        else:
            expected = (
                adafruit_msa3xx.Range.RANGE_4_G,
                adafruit_msa3xx.DataRate.RATE_125_HZ,
                adafruit_msa3xx.Mode.NORMAL,
            )

        if item["baseline"] != expected:
            raise RuntimeError(
                f"{name} startup configuration mismatch: "
                f"expected={expected}, actual={item['baseline']}"
            )

        devices[name] = item
        print(
            f"# DEVICE {name} CH{channel} {model} "
            f"address={hex(address)} config={item['baseline']}",
            flush=True,
        )

    time.sleep(0.3)
    return devices


def check_configuration(devices):
    for name in ORDER:
        item = devices[name]
        current = configuration(item)
        if current != item["baseline"]:
            raise RuntimeError(
                f"{name} CONFIG_CHANGED "
                f"{item['baseline']} -> {current}"
            )


def read_one(item, origin):
    started = time.monotonic()
    sensor = item["sensor"]
    successful_midpoint = None
    if item["name"] == "RH":
        successful_midpoint, values = sensor.read_sample()
    else:
        values = tuple(sensor.acceleration)
        if item["name"] != "HS":
            values += tuple(sensor.gyro)
    finished = time.monotonic()

    expected_length = 3 if item["name"] == "HS" else 6
    if len(values) != expected_length or any(
        v is None or not math.isfinite(v) for v in values
    ):
        raise ValueError("Missing/non-finite data")
    if all(v == 0 for v in values):
        raise ValueError("ALL_ZERO: sensor may have reset")

    midpoint = (
        successful_midpoint if successful_midpoint is not None
        else (started + finished) / 2
    ) - origin
    return midpoint, tuple(float(v) for v in values)


def collect(devices, args, health=False):
    selected, action_seconds, instruction = TASKS.get(
        args.task, (ORDER, 0, "")
    )
    # Retain head data during hand tasks for simultaneous-motion analysis.
    if args.task in ("chop", "stir", "flip", "twist", "hands_other"):
        selected = ORDER
    total = args.seconds if health else action_seconds + 4
    period = 1 / args.hz

    # Only selected sensors are stored; storage is bounded per trial.
    rows = []
    max_rows = math.ceil(total * args.hz) + 5
    near_limit = {name: 0 for name in ORDER}
    count = skipped = 0
    max_read_ms = 0.0
    max_gap = 0.0
    first_t = last_t = None
    failure = ""
    previous_phase = None
    twist_number = 0

    if not health:
        print("# INSTRUCTION:", instruction)
    input("Ready? Press Enter. ")
    try:
        prepare_trial(devices)
    except Exception as exc:
        rh_report(devices["RH"], "PREFLIGHT_FAILED")
        print("# PREFLIGHT_FAILED", ascii(str(exc)), flush=True)
        print("# No trial started. No action needed.", flush=True)
        return False

    for value in (3, 2, 1):
        print(f"# COUNTDOWN {value}", flush=True)
        time.sleep(1)

    start = time.monotonic()
    deadline = start
    next_check = 0.0

    try:
        check_configuration(devices)
        start = time.monotonic()
        deadline = start
        while True:
            delay = deadline - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            t = time.monotonic() - start
            if t >= total:
                break

            phase = (
                "HEALTH" if health else
                "PRE" if t < 2 else
                "ACTION" if t < 2 + action_seconds else "POST"
            )

            if phase != previous_phase:
                messages = {
                    "PRE": "Hold neutral and still for 2 seconds.",
                    "ACTION": instruction,
                    "POST": "Stop; hold still for 2 seconds.",
                    "HEALTH": "Read all four sensors; follow test plan.",
                }
                print(f"# {phase}: {messages[phase]}", flush=True)
                previous_phase = phase

            if not health and args.task == "twist" and phase == "ACTION":
                action_t = t - 2
                cue_times = (0.0, 2.5, 5.0)
                if twist_number < 3 and action_t >= cue_times[twist_number]:
                    twist_number += 1
                    print(
                        f"# TWIST {twist_number}/3 NOW t={t:.3f}",
                        flush=True,
                    )

            # One thread, fixed sequence. No competing bus readers.
            readings = {}
            cycle_start = time.monotonic()
            for name in ORDER:
                try:
                    readings[name] = read_one(devices[name], start)
                except Exception as exc:
                    raise RuntimeError(f"{name}: {exc}") from exc

                values = readings[name][1]
                # Warning only: close to configured per-axis full scale.
                if (
                    max(abs(v) for v in values[:3]) >= 0.98 * 4 * 9.80665
                    or max((abs(v) for v in values[3:]), default=0.0) >=
                    0.98 * math.radians(2000)
                ):
                    near_limit[name] += 1

            max_read_ms = max(
                max_read_ms, (time.monotonic() - cycle_start) * 1000
            )
            count += 1
            if first_t is None:
                first_t = t
            if last_t is not None:
                max_gap = max(max_gap, t - last_t)
            last_t = t

            if not health:
                if len(rows) >= max_rows:
                    raise RuntimeError("Buffer bound exceeded")
                rows.append(
                    (t, phase, tuple(readings[n] for n in selected))
                )

            if t >= next_check:
                check_configuration(devices)
                if health:
                    parts = []
                    for name in ORDER:
                        values = readings[name][1]
                        a = math.sqrt(sum(v*v for v in values[:3]))
                        if name == "HS":
                            parts.append(f"{name}:a={a:.2f},g=NA")
                        else:
                            g = math.sqrt(sum(v*v for v in values[3:]))
                            parts.append(f"{name}:a={a:.2f},g={g:.2f}")
                    print(
                        f"# HEALTH {t:.1f}s " + " | ".join(parts),
                        flush=True,
                    )
                next_check = t + 1

            deadline += period
            now = time.monotonic()
            if now > deadline:
                missed = int((now - deadline) / period) + 1
                skipped += missed
                deadline += missed * period

        check_configuration(devices)

    except KeyboardInterrupt:
        failure = "USER_INTERRUPTED"
    except Exception as exc:
        failure = str(exc)
        rh_report(devices["RH"], "AT_FAULT")

    rate = (
        (count - 1) / (last_t - first_t)
        if count > 1 and last_t > first_t else 0
    )

    # Print after sampling, so raw output cannot delay sensor polling.
    if not health:
        print(
            f"# DATA_BEGIN task={args.task} "
            f"status={'INVALID' if failure else 'OK'}"
        )
        print("# NOTE", ascii(args.note))
        print("# units: acc=m/s^2 including gravity; gyro=rad/s")
        print("# sensor t_s = midpoint of sequential accel/gyro reads")
        fields = ["t_s", "phase"]
        for name in selected:
            fields += [
                f"{name}_{field}"
                for field in (
                    ("t_s", "ax", "ay", "az")
                    if name == "HS"
                    else ("t_s", "ax", "ay", "az", "gx", "gy", "gz")
                )
            ]
        print(",".join(fields))

        for t, phase, samples in rows:
            columns = [f"{t:.4f}", phase]
            for midpoint, values in samples:
                columns.append(f"{midpoint:.4f}")
                columns.extend(f"{v:.4f}" for v in values)
            print(",".join(columns))

        print("# DATA_END")

    print(
        f"# SUMMARY task={args.task} "
        f"status={'INVALID' if failure else 'OK'} "
        f"samples={count} actual_hz={rate:.2f} "
        f"skipped_slots={skipped} "
        f"max_gap_ms={max_gap * 1000:.2f} "
        f"max_four_sensor_read_ms={max_read_ms:.2f} "
        f"near_limit={near_limit}",
        flush=True,
    )
    rh = devices["RH"]["sensor"]
    print(
        f"# RH_IO cumulative_retries={rh.retry_count} "
        f"cumulative_recovered_reads={rh.recovered_reads}",
        flush=True,
    )
    if rh.retry_count:
        print(
            "# TIMING_REVIEW_REQUIRED: retries occurred in this run; "
            "inspect sensor timestamps and sample gaps.",
            flush=True,
        )

    if failure:
        print("# FAULT", ascii(failure), flush=True)
        print("# Do not use this trial for threshold fitting.")
        return False

    if rate < args.hz * 0.9:
        print("# WARNING: actual rate below target; inspect timing.")

    if not health:
        observation = input(
            "Actual count / mistakes / notes (English or numbers): "
        )
        print("# OBSERVED", ascii(observation), flush=True)

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=["health", *TASKS], required=True)
    parser.add_argument("--hz", type=int, choices=(20, 25), default=25)
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--seconds", type=int, default=60,
                        help="Duration for health test only")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    if not 1 <= args.trials <= 10:
        parser.error("trials must be 1-10")
    if not 10 <= args.seconds <= 300:
        parser.error("health seconds must be 10-300")

    i2c = board.I2C()
    try:
        devices = initialize(i2c)
        for trial in range(1, args.trials + 1):
            print(f"\n# TRIAL {trial}/{args.trials}", flush=True)
            if not collect(devices, args, health=args.task == "health"):
                break
    finally:
        i2c.deinit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n# STOPPED")
    except Exception as exc:
        print("# STARTUP_ERROR", ascii(str(exc)))
        raise SystemExit(1)
