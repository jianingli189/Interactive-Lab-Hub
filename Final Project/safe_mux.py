"""Process-local multiplexer lock fix; never modifies installed packages."""
import time


def install(module):
    cls = module.TCA9548A_Channel
    if getattr(cls, '_kitchen_safe_lock', False):
        return

    def try_lock(self):
        upstream = self.tca.i2c
        deadline = time.monotonic() + 0.5
        while not upstream.try_lock():
            if time.monotonic() >= deadline:
                raise TimeoutError('MUX upstream lock unavailable for 0.5 seconds')
            time.sleep(0.001)
        try:
            upstream.writeto(self.tca.address, self.channel_switch)
        except BaseException:
            upstream.unlock()
            raise
        return True

    def unlock(self):
        try:
            self.tca.i2c.writeto(self.tca.address, b'\x00')
        finally:
            self.tca.i2c.unlock()

    cls.try_lock = try_lock
    cls.unlock = unlock
    cls._kitchen_safe_lock = True
