
#!/usr/bin/env python3

import json
import os
import uuid
import time
import statistics

import board
import adafruit_tca9548a
import adafruit_vcnl4040
from adafruit_apds9960.apds9960 import APDS9960

import paho.mqtt.client as mqtt


# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    0: {
        "name": "Chopsticks",
        "id": "chopsticks",
        "type": "apds9960",
        "pickup": 81,
        "return": 150,
    },
    1: {
        "name": "Knife",
        "id": "knife",
        "type": "apds9960",
        "pickup": 68,
        "return": 126,
    },
    5: {
        "name": "Spatula",
        "id": "spatula",
        "type": "apds9960",
        "pickup": 83,
        "return": 155,
    },
    6: {
        "name": "Salt Shaker",
        "id": "salt_shaker",
        "type": "apds9960",
        "pickup": 80,
        "return": 160,
    },
    7: {
        "name": "Pepper Grinder",
        "id": "pepper_grinder",
        "type": "vcnl4040",
        "pickup": 120,
        "return": 300,
    },
}

SAMPLE_INTERVAL = 0.15
DEBOUNCE_COUNT = 3
STATE_INTERVAL = 1.0

# MQTT
MQTT_HOST = os.environ.get("KITCHEN_MQTT_HOST", "farlab.infosci.cornell.edu")
MQTT_PORT = 1883
MQTT_PREFIX = os.environ.get("KITCHEN_MQTT_PREFIX", "IDD/jianing-kitchen/utensil")
MQTT_EVENT_TOPIC = MQTT_PREFIX + "/event"
MQTT_STATE_TOPIC = MQTT_PREFIX + "/state"
SESSION_ID = uuid.uuid4().hex
message_seq = 0
sensor_valid = {}
last_success = {}


# ============================================================
# MQTT INITIALIZATION
# ============================================================

mqtt_connected = False


def on_connect(client, userdata, flags, reason_code, properties):
    global mqtt_connected

    mqtt_connected = not reason_code.is_failure

    if mqtt_connected:
        print("[MQTT] Connected to broker.", flush=True)
    else:
        print(
            f"[MQTT] Connection failed: {reason_code}",
            flush=True,
        )


def on_disconnect(client, userdata, disconnect_flags,
                  reason_code, properties):
    global mqtt_connected
    mqtt_connected = False
    print(
        f"[MQTT] Disconnected: {reason_code}",
        flush=True,
    )


mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="kitchen-utensils-" + SESSION_ID[:8],
)

mqtt_client.username_pw_set(
    os.environ.get("KITCHEN_MQTT_USER", "idd"),
    os.environ.get("KITCHEN_MQTT_PASSWORD"),
)
mqtt_client.max_queued_messages_set(20)
mqtt_client.reconnect_delay_set(1, 10)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect


def publish_message(topic, payload, retain=False):
    global message_seq
    if not mqtt_connected:
        return False
    message_seq += 1
    payload = {**payload, "session_id": SESSION_ID, "seq": message_seq}

    info = mqtt_client.publish(
        topic,
        json.dumps(payload),
        qos=1,
        retain=retain,
    )

    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        print(
            f"[MQTT] Publish error: {info.rc}",
            flush=True,
        )
        return False

    return True


def publish_event(ch, present, value):
    config = CONFIG[ch]

    payload = {
        "utensil": config["id"],
        "channel": ch,
        "event": "returned" if present else "picked_up",
        "present": present,
        "proximity": value,
        "timestamp": time.time(),
    }

    if publish_message(MQTT_EVENT_TOPIC, payload):
        print(
            f"[MQTT] Queued: {config['id']} "
            f"{payload['event']}",
            flush=True,
        )


def publish_states(states):
    payload = {
        "timestamp": time.time(),
        "utensils": {
            CONFIG[ch]["id"]: {
                "present": present,
                "channel": ch,
                "valid": sensor_valid.get(ch, False),
                "last_success": last_success.get(ch),
            }
            for ch, present in states.items()
        },
    }

    publish_message(
        MQTT_STATE_TOPIC,
        payload,
        retain=False,
    )


# ============================================================
# SENSOR INITIALIZATION
# ============================================================

def initialize_sensors():
    print("\n=== SENSOR CONNECTION STATUS ===")

    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)

    sensors = {}

    for ch, config in CONFIG.items():
        try:
            if config["type"] == "vcnl4040":
                sensor = adafruit_vcnl4040.VCNL4040(
                    tca[ch]
                )
            else:
                sensor = APDS9960(tca[ch])
                sensor.enable_proximity = True

            # Verify that the sensor responds
            sensor.proximity

            sensors[ch] = sensor

            print(
                f"CH{ch} | {config['name']:<15} "
                "| Connected",
                flush=True,
            )

        except Exception as e:
            print(
                f"CH{ch} | {config['name']}: "
                f"Connection ERROR - {e}",
                flush=True,
            )

    return i2c, sensors


def stable_reading(sensor, samples=5):
    values = []

    for _ in range(samples):
        values.append(sensor.proximity)
        time.sleep(0.05)

    return statistics.median(values)


# ============================================================
# MAIN DETECTION
# ============================================================

def run_detection(sensors):
    states = {}
    candidates = {}
    counts = {}

    print("\n=== INITIAL UTENSIL STATES ===")

    time.sleep(1)

    for ch, sensor in sensors.items():
        config = CONFIG[ch]

        try:
            value = stable_reading(sensor)

            midpoint = (
                config["pickup"] + config["return"]
            ) / 2

            present = value >= midpoint

            states[ch] = present
            sensor_valid[ch] = True
            last_success[ch] = time.time()
            candidates[ch] = None
            counts[ch] = 0

            status = "Present" if present else "Removed"

            print(
                f"CH{ch} | {config['name']}: "
                f"{status} (Reading: {value:.0f})",
                flush=True,
            )

        except Exception as e:
            print(
                f"CH{ch} | Initialization ERROR: {e}",
                flush=True,
            )

    if not states:
        print("ERROR: No active sensors.")
        return

    print("\n=== UTENSIL DETECTION STARTED ===")
    print("Press Ctrl+C to stop.\n")

    last_state_publish = 0.0

    try:
        while True:
            for ch, sensor in sensors.items():
                if ch not in states:
                    continue

                config = CONFIG[ch]

                try:
                    value = sensor.proximity
                    sensor_valid[ch] = True
                    last_success[ch] = time.time()
                    current = states[ch]

                    # Hysteresis
                    if current:
                        observed = not (
                            value <= config["pickup"]
                        )
                    else:
                        observed = (
                            value >= config["return"]
                        )

                    # Debounce
                    if observed != current:

                        if candidates[ch] == observed:
                            counts[ch] += 1
                        else:
                            candidates[ch] = observed
                            counts[ch] = 1

                        if counts[ch] >= DEBOUNCE_COUNT:
                            states[ch] = observed
                            candidates[ch] = None
                            counts[ch] = 0

                            timestamp = time.strftime(
                                "%H:%M:%S"
                            )

                            event = (
                                "returned"
                                if observed
                                else "picked up"
                            )

                            print(
                                f"[{timestamp}] "
                                f"{config['name']} "
                                f"{event} (CH{ch})",
                                flush=True,
                            )

                            publish_event(
                                ch,
                                observed,
                                value,
                            )

                    else:
                        candidates[ch] = None
                        counts[ch] = 0

                except Exception as e:
                    sensor_valid[ch] = False
                    candidates[ch] = None
                    counts[ch] = 0
                    print(
                        f"CH{ch} ({config['name']}) "
                        f"read ERROR: {e}",
                        flush=True,
                    )

            # Periodic state broadcast
            now = time.monotonic()

            if now - last_state_publish >= STATE_INTERVAL:
                publish_states(states)
                last_state_publish = now

            time.sleep(SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        print("\nUtensil detection stopped.")

    finally:
        print("\n=== FINAL UTENSIL STATES ===")

        for ch, present in states.items():
            status = "Present" if present else "Removed"

            print(
                f"CH{ch} | {CONFIG[ch]['name']}: "
                f"{status}"
            )


# ============================================================
# ENTRY POINT
# ============================================================

def main():
    i2c = None

    try:
        print("Connecting to MQTT broker...")

        if not os.environ.get("KITCHEN_MQTT_PASSWORD"):
            raise RuntimeError("Set KITCHEN_MQTT_PASSWORD")

        mqtt_client.connect(
            MQTT_HOST,
            MQTT_PORT,
            keepalive=60,
        )

        mqtt_client.loop_start()

        i2c, sensors = initialize_sensors()
        run_detection(sensors)

    except KeyboardInterrupt:
        print("\nProgram interrupted.")

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        print("\nShutting down...")

        mqtt_client.disconnect()
        mqtt_client.loop_stop()

        if i2c is not None:
            i2c.deinit()

        print("Program exited.")


if __name__ == "__main__":
    main()
