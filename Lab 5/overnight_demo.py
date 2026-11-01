import cv2
import json
import time
import subprocess
from datetime import datetime
from ultralytics import YOLO


# ============================================================
# SETTINGS
# ============================================================

MODEL_PATH = "yolo26n_ncnn_model"

# Compressed overnight demo
RUN_DURATION = 60
SAMPLE_INTERVAL = 3

CONFIDENCE_THRESHOLD = 0.40

# COCO class ID for cell phone
CELL_PHONE_CLASS = 67

# Each observation uses multiple frames
NUM_FRAMES = 5
REQUIRED_DETECTIONS = 2
FRAME_DELAY = 0.2

LOG_FILE = "night_log.jsonl"


# ============================================================
# SETUP
# ============================================================

print("Loading YOLO model...")
model = YOLO(MODEL_PATH)

print("Opening camera...")
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    raise RuntimeError("Could not open camera.")

print("Camera ready.")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def timestamp():
    return datetime.now().isoformat(timespec="seconds")


def format_time(iso_time):
    dt = datetime.fromisoformat(iso_time)
    return dt.strftime("%-I:%M:%S %p")


def write_log(event):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


def detect_phone():

    detection_count = 0
    best_confidence = None

    for _ in range(NUM_FRAMES):

        success, frame = cap.read()

        if not success:
            print("WARNING: Could not read camera frame.")
            time.sleep(FRAME_DELAY)
            continue

        results = model(
            frame,
            imgsz=320,
            conf=CONFIDENCE_THRESHOLD,
            classes=[CELL_PHONE_CLASS],
            verbose=False
        )

        detected_this_frame = False

        for result in results:
            for box in result.boxes:

                confidence = float(box.conf.item())
                detected_this_frame = True

                if (
                    best_confidence is None
                    or confidence > best_confidence
                ):
                    best_confidence = confidence

        if detected_this_frame:
            detection_count += 1

        time.sleep(FRAME_DELAY)

    phone_detected = detection_count >= REQUIRED_DETECTIONS

    print(
        f"    Detection vote: "
        f"{detection_count}/{NUM_FRAMES} frames"
    )

    return phone_detected, best_confidence


def speak(text):
    """
    Try to speak the morning report.

    Uses the system 'espeak' command if available.
    If speech is unavailable, the report is still printed.
    """

    print()
    print("SPEAKING MORNING REPORT:")
    print(text)
    print()

    try:
        subprocess.run(
            ["espeak", "-s", "145", text],
            check=False
        )

    except FileNotFoundError:
        print(
            "Speech unavailable: espeak is not installed. "
            "The report was printed instead."
        )


# ============================================================
# PREPARE LOG
# ============================================================

# Start each demo with a fresh overnight log.
open(LOG_FILE, "w").close()


# ============================================================
# INITIAL STATE
# ============================================================

state = "phone_in_dock"

possible_use_start = None
possible_use_periods = []

monitoring_start = timestamp()

start_event = {
    "time": monitoring_start,
    "event": "monitoring_started",
    "state": state
}

write_log(start_event)


print()
print("======================================")
print("       PHONE SLEEP CHECK")
print("======================================")
print()
print("Phone checked in.")
print(f"Monitoring for {RUN_DURATION} seconds.")
print(f"Sampling every {SAMPLE_INTERVAL} seconds.")
print()


# ============================================================
# MONITORING LOOP
# ============================================================

start_monotonic = time.monotonic()

try:

    while time.monotonic() - start_monotonic < RUN_DURATION:

        phone_detected, confidence = detect_phone()
        now = timestamp()

        # ----------------------------------------------------
        # PHONE PRESENT
        # ----------------------------------------------------

        if phone_detected:

            if state == "possible_phone_use":

                possible_use_end = now

                possible_use_periods.append({
                    "start": possible_use_start,
                    "end": possible_use_end
                })

                event = {
                    "time": now,
                    "event": "phone_returned",
                    "phone_detected": True,
                    "confidence": round(confidence, 3),
                    "state": "phone_in_dock",
                    "possible_use_started": possible_use_start
                }

                write_log(event)

                print(
                    f"[{now}] PHONE RETURNED "
                    f"(confidence {confidence:.2f})"
                )

                state = "phone_in_dock"
                possible_use_start = None

            else:

                event = {
                    "time": now,
                    "event": "observation",
                    "phone_detected": True,
                    "confidence": round(confidence, 3),
                    "state": "phone_in_dock"
                }

                write_log(event)

                print(
                    f"[{now}] phone present "
                    f"(confidence {confidence:.2f})"
                )

        # ----------------------------------------------------
        # PHONE ABSENT
        # ----------------------------------------------------

        else:

            if state == "phone_in_dock":

                possible_use_start = now
                state = "possible_phone_use"

                event = {
                    "time": now,
                    "event": "phone_missing",
                    "phone_detected": False,
                    "confidence": None,
                    "state": state
                }

                write_log(event)

                print(
                    f"[{now}] PHONE MISSING "
                    "-> possible phone-use period started"
                )

            else:

                event = {
                    "time": now,
                    "event": "observation",
                    "phone_detected": False,
                    "confidence": None,
                    "state": state
                }

                write_log(event)

                print(
                    f"[{now}] phone still missing "
                    "-> possible phone-use period continues"
                )

        time.sleep(SAMPLE_INTERVAL)


# ============================================================
# CLEAN EXIT IF USER PRESSES CTRL-C
# ============================================================

except KeyboardInterrupt:

    print()
    print("Monitoring stopped manually.")


# ============================================================
# END MONITORING
# ============================================================

finally:

    monitoring_end = timestamp()

    # If the phone is still absent when monitoring ends,
    # close the final possible-use period at the end time.
    if (
        state == "possible_phone_use"
        and possible_use_start is not None
    ):

        possible_use_periods.append({
            "start": possible_use_start,
            "end": monitoring_end
        })

    stop_event = {
        "time": monitoring_end,
        "event": "monitoring_stopped",
        "state": state,
        "possible_phone_use_periods": possible_use_periods
    }

    write_log(stop_event)

    cap.release()
    cv2.destroyAllWindows()

    print()
    print("======================================")
    print("       MONITORING COMPLETE")
    print("======================================")
    print()
    print(f"Night log saved to {LOG_FILE}")


# ============================================================
# GENERATE MORNING REPORT
# ============================================================

if len(possible_use_periods) == 0:

    report = (
        "Good morning! "
        f"Your phone was checked in at "
        f"{format_time(monitoring_start)}. "
        "I did not observe any possible phone-use periods "
        "during the night. "
        f"Monitoring ended at {format_time(monitoring_end)}."
    )

else:

    period_sentences = []

    for period in possible_use_periods:

        start_text = format_time(period["start"])
        end_text = format_time(period["end"])

        period_sentences.append(
            f"from {start_text} to {end_text}"
        )

    periods_text = ", and ".join(period_sentences)

    if len(possible_use_periods) == 1:
        event_text = "one possible phone-use period"
    else:
        event_text = (
            f"{len(possible_use_periods)} "
            "possible phone-use periods"
        )

    report = (
        "Good morning! "
        f"Your phone was checked in at "
        f"{format_time(monitoring_start)}. "
        f"I noticed {event_text}: "
        f"{periods_text}. "
        f"Monitoring ended at "
        f"{format_time(monitoring_end)}."
    )


# ============================================================
# PRINT + SPEAK REPORT
# ============================================================

print()
print("======================================")
print("          MORNING REPORT")
print("======================================")
print()
print(report)
print()

speak(report)