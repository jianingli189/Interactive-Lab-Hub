"""Adaptive checks; no fabricated samples, no permanent per-sensor disable."""
import time

class RecoveryReader:
    DELAYS = (0.5, 1, 2, 5)
    def __init__(self, hw, emit, clock=time.monotonic):
        self.hw, self.emit, self.clock = hw, emit, clock
        self.states = {}
        self.failures = 0

    def restore(self, item, actual):
        hw = self.hw
        name = item['name']
        if name in ('LH', 'HF'):
            if actual[0] != item['baseline'][0]:
                raise RuntimeError('LSM identity mismatch; configuration not written')
            with hw.I2CDevice(item['bus'], item['address'], probe=False) as dev:
                for reg, val in ((0x12,0x44),(0x10,0x48),(0x11,0x4C)):
                    dev.write(bytes((reg,val)))
            time.sleep(0.1)
        elif name == 'RH':
            hw.rh_configure(item)
        elif name == 'HS':
            sensor = item['sensor']
            sensor.range, sensor.data_rate, sensor.power_mode = item['baseline']
        if hw.configuration(item) != item['baseline']:
            raise RuntimeError('Configuration readback still differs after restore')

    def read(self, name, item, origin):
        now = self.clock()
        s = self.states.setdefault(name,dict(next=0, failures=0, bad=False, good=0, checked=-100, healthy=None))
        if now < s['next']:
            return None
        recovering = s['bad']
        stage = 'check_config'
        try:
            if recovering and s['good'] == 0:
                self.emit('recovery_attempt',sensor=name,attempt=s['failures'])
            if s['good'] == 0 or now - s['checked'] >= 1:
                try:
                    actual = self.hw.configuration(item)
                except RuntimeError:
                    # BNO configuration() raises for readable but invalid states.
                    # Re-read identity before any configuration writes; I/O errors
                    # still propagate into the normal bounded backoff.
                    if name != 'RH' or not recovering:
                        raise
                    state = self.hw.rh_state(item)
                    if state[0] != 0 or state[1] != 0xA0:
                        raise RuntimeError('RH page/identity invalid; configuration not written')
                    stage = 'restore_config'
                    self.restore(item, (state[1], state[2]))
                    self.emit('recovery_configured', sensor=name)
                    actual = self.hw.configuration(item)
                if actual != item['baseline']:
                    print('# CONFIG_DIFF',name,'actual=',actual,'expected=',item['baseline'],flush=True)
                    if not recovering:
                        raise RuntimeError('Configuration changed: ' + repr(actual))
                    stage = 'restore_config'
                    self.restore(item, actual)
                    self.emit('recovery_configured',sensor=name)
                s['checked'] = self.clock()
            stage = 'read_sample'
            sample = self.hw.read_one(item, origin)
            s['good'] += 1
            if s['good'] < 5:
                return None
            if recovering:
                self.emit('sensor_recovered',sensor=name)
            s['bad'] = False
            if recovering:
                s['failures'] = 0
            if s['healthy'] is None:
                s['healthy'] = self.clock()
            if self.clock() - s['healthy'] >= 30:
                s['failures'] = 0
            return sample
        except Exception as exc:
            self.failures += 1
            s['failures'] += 1
            delay = self.DELAYS[min(s['failures']-1,len(self.DELAYS)-1)]
            s.update(bad=True,good=0,healthy=None,next=self.clock()+delay)
            self.emit('sensor_fault',sensor=name,message=f'stage={stage}: {exc}; next check in {delay:g}s')
            return None
