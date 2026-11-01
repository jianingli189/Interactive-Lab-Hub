# Evidence provenance

- `qwiic_complete_terminal.txt`: user-supplied Pi terminal transcript, copied without editing. Run ID: `abc2f8fb-bd2c-44fe-9f6b-7be87345a23a`.
- `demo_complete_from_transcript.jsonl`: 23 printed event dictionaries parsed from that transcript and serialized as valid JSON Lines. Values are preserved; no observations or timestamps were invented. This is a transcript-derived copy, not a directly downloaded Pi log. The original `demo_complete.jsonl` remains on the Pi until transferred.
- `morning_report.txt`: exact report field from the recorded `morning_report` event.
- `qwiic_test_aborted_terminal.txt`: earlier Ctrl-C-interrupted test; retained separately as debugging evidence.

Checked: start and end button events, two missing/return intervals, monotonic durations, total 29.223 seconds, and report event. The transcript ends after printing the speech text; it does not prove audible output or completion of audio playback. The user reports recording a video, which has not yet been supplied for inspection.

Source transcript SHA-256: `2df4250fa2de62f6d105d39b661e64e25db8bca2a3bccc29619ed0c4e3749ee8`.
