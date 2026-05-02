# # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# # SPDX-License-Identifier: MIT

import pykit_explorer
import math
from analog_io import AnalogInput
import adafruit_mpu6050
from emg_processor import EMGProcessor
from pulse_sensor import PulseSensor
from imu_sensor import IMUSensor

#sensor loop
pulse = PulseSensor(pykit_explorer.board.A5)
emg_sensor = AnalogInput(pykit_explorer.board.A4)
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