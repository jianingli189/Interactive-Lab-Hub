# Sensor bridge

See [the complete startup guide](../README.md) for current deployment, all four terminals, demo/classifier selection and shutdown. Run this bridge on the motion Pi, not on the Mac. It starts exactly one motion child process and optionally subscribes to utensil MQTT. The Mac forwards port 18765 to Pi port 8765; the browser consumes `/events` (SSE). `/health` checks bridge reachability, not proof of healthy sensors.

`--demo` selects generic-motion demonstration including single-hand fallback. Without it the original experimental classifier still requires both hands. `--mqtt` requires `KITCHEN_MQTT_PASSWORD`; do not commit credentials. `--replay`/fixtures are debugging data, not live observations; inspect `--help` for supported arguments.
