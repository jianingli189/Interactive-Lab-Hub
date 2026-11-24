"""Validate utensil MQTT; preserve unknown/failed sensors instead of guessing."""
import json
import os
import time
import uuid

IDS = {'chopsticks', 'knife', 'spatula', 'salt_shaker', 'pepper_grinder'}


def normalize_state(payload, received_at):
    if not isinstance(payload, dict) or not isinstance(payload.get('utensils'), dict):
        raise ValueError('Missing utensils map')
    result = {}
    for name in IDS:
        raw = payload['utensils'].get(name)
        if not isinstance(raw, dict) or type(raw.get('present')) is not bool:
            result[name] = {'present': None, 'valid': False, 'healthKnown': False}
        else:
            valid = raw.get('valid')
            result[name] = {'present': raw['present'] if valid is not False else None,
                            'valid': valid is not False,
                            'healthKnown': type(valid) is bool,
                            'channel': raw.get('channel')}
    return {'receivedAt': received_at, 'timestamp': payload.get('timestamp'),
            'utensils': result}


def start_mqtt(hub, host, prefix):
    import paho.mqtt.client as mqtt
    password = os.environ.get('KITCHEN_MQTT_PASSWORD')
    if not password:
        raise RuntimeError('Set KITCHEN_MQTT_PASSWORD before enabling MQTT')
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id='kitchen-web-' + uuid.uuid4().hex[:12])
    client.username_pw_set(os.environ.get('KITCHEN_MQTT_USER', 'idd'), password)
    client.reconnect_delay_set(1, 10)
    client.max_queued_messages_set(20)

    def status(connected):
        with hub.lock:
            hub.mqtt_connected = connected
            if not connected:
                hub.utensils = None
        hub.broadcast('utensil_link', {'connected': connected})

    def connected(c, userdata, flags, reason, properties):
        status(not reason.is_failure)
        if not reason.is_failure:
            c.subscribe(prefix.rstrip('/') + '/state', qos=1)

    def disconnected(c, userdata, flags, reason, properties):
        status(False)

    def message(c, userdata, msg):
        # State is authoritative for display; never replay pickup events as commands.
        if msg.retain:
            return
        try:
            payload = json.loads(msg.payload)
            state = normalize_state(payload, int(time.time() * 1000))
        except (ValueError, TypeError, UnicodeDecodeError):
            return
        with hub.lock:
            hub.utensils = state
        hub.broadcast('utensil', state)

    client.on_connect = connected
    client.on_disconnect = disconnected
    client.on_message = message
    client.connect_async(host, 1883, keepalive=15)
    client.loop_start()
    return client
