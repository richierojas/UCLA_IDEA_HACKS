# # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# # SPDX-License-Identifier: MIT

import pykit_explorer
import math
from analog_io import AnalogInput
import adafruit_mpu6050

# EMG processing
class EMGProcessor:
    def __init__(self):
        self.filtered = 0
        self.alpha = 0.2

    def process(self, envelope_value):
        self.filtered = (1 - self.alpha) * self.filtered + self.alpha * envelope_value

        activation = self.filtered / 50000
        activation = max(0, min(1, activation))

        return activation
# Pulse processing
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

# IMU processing
class IMUSensor:
    def __init__(self):
        self.i2c = pykit_explorer.board.I2C()
        self.mpu = adafruit_mpu6050.MPU6050(self.i2c)

    def fall_detected(self):
        ax, ay, az = self.mpu.acceleration

        total_accel = math.sqrt(ax**2 + ay**2 + az**2)

        free_fall = total_accel < 5
        impact = total_accel > 13

        return free_fall or impact

#sensor loop
pulse = PulseSensor(pykit_explorer.board.A0)
emg_sensor = AnalogInput(pykit_explorer.board.A1)
emg_processor = EMGProcessor()
imu = IMUSensor()

print("Starting sensor loop")

# Main loop
while True:
    emg_value = emg_sensor.value
    activation = emg_processor.process(emg_value)
    bpm = pulse.get_bpm(pulse.read())
    fall = imu.fall_detected()

    print("BPM:", bpm)
    print("Fall detected:", fall)
    print("EMG activation:", activation)

    pykit_explorer.time.sleep(0.02)