class PulseSensor:
    def __init__(self, pin):
        self.sensor = AnalogInput(pin)

        self.threshold = 30000
        self.last_beat_time = 0
        self.bpm = 0

        self.alpha = 0.1
        self.baseline = 0

    def read(self):
        return self.sensor.value

    def get_bpm(self, value):
        now = pykit_explorer.time.monotonic()

        self.baseline = (1 - self.alpha) * self.baseline + self.alpha * value
        signal = value - self.baseline

        if signal > self.threshold and (now - self.last_beat_time) > 0.5:

            if self.last_beat_time != 0:
                interval = now - self.last_beat_time

                if 0.3 < interval < 2.0:
                    instant = 60 / interval
                    self.bpm = 0.8 * self.bpm + 0.2 * instant

            self.last_beat_time = now

        return self.bpm