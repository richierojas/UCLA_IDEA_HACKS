# # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# # SPDX-License-Identifier: MIT

import pykit_explorer
import math
from analog_io import AnalogInput
import adafruit_mpu6050

# =========================================================
# SENSORS
# =========================================================

emg = AnalogInput(pykit_explorer.board.A4)
pulse = AnalogInput(pykit_explorer.board.A5)

i2c = pykit_explorer.board.I2C()
mpu = adafruit_mpu6050.MPU6050(i2c)

print("✓ Sensors initialized")

# =========================================================
# HELPERS
# =========================================================

def read_avg(sensor, samples=5):
    total = 0
    for _ in range(samples):
        total += sensor.raw
        pykit_explorer.time.sleep(0.001)
    return total / samples

def clamp(x, a, b):
    return max(a, min(b, x))

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# =========================================================
# EMG CALIBRATION
# =========================================================

print("Calibrating EMG... stay relaxed")

rest_vals = [read_avg(emg, 10) for _ in range(30)]
rest = sum(rest_vals) / len(rest_vals)

print("Baseline locked:", int(rest))

REST_DELTA = 1500
MAX_DELTA = 5000

peak = 0
DECAY = 0.96

# =========================================================
# PULSE SETTINGS (FIXED)
# =========================================================

beat_times = []
last_beat = 0

bpm = 75.0
prev_bpm = 75.0

BUFFER_SIZE = 8
buffer = []

THRESHOLD = 25
REFRACTORY = 0.45

pulse_base = 0
alpha = 0.1

# =========================================================
# FALL SETTINGS
# =========================================================

HIGH_G = 13.0
LOW_G = 5.0

print("✓ SYSTEM STARTED")

# =========================================================
# MAIN LOOP
# =========================================================

while True:

    now = pykit_explorer.time.monotonic()

    # =====================================================
    # FALL DETECTION
    # =====================================================

    ax, ay, az = mpu.acceleration
    accel_mag = math.sqrt(ax**2 + ay**2 + az**2)

    fall_detected = accel_mag > HIGH_G or accel_mag < LOW_G

    # =====================================================
    # EMG PROCESSING
    # =====================================================

    emg_value = emg.raw
    emg_delta = abs(emg_value - rest)

    if emg_delta > peak:
        peak = emg_delta
    else:
        peak *= DECAY

    emg_strength = map_range(peak, REST_DELTA, MAX_DELTA, 0, 5)
    emg_strength = clamp(emg_strength, 0, 5)

    # =====================================================
    # PULSE PROCESSING (STABLE BPM FIX)
    # =====================================================

    raw = pulse.raw

    # moving baseline filter
    pulse_base = (1 - alpha) * pulse_base + alpha * raw

    signal = raw - pulse_base

    buffer.append(signal)
    if len(buffer) > BUFFER_SIZE:
        buffer.pop(0)

    smooth = sum(buffer) / len(buffer)

    # =====================================================
    # BEAT DETECTION
    # =====================================================

    if smooth > THRESHOLD:

        if now - last_beat > REFRACTORY:

            interval = now - last_beat
            last_beat = now

            if 0.4 < interval < 1.2:

                instant_bpm = 60 / interval

                if 40 < instant_bpm < 180:
                    bpm = 0.85 * bpm + 0.15 * instant_bpm

    # slow decay only when no signal
    if now - last_beat > 3:
        bpm *= 0.995

    # =====================================================
    # FALL RESPONSE
    # =====================================================

    if fall_detected:
        print("\n🚨 FALL DETECTED! SYSTEM STOPPED")

        print(f"Previous BPM: {prev_bpm:.1f}")
        print(f"Current BPM: {bpm:.1f}")

        if bpm > prev_bpm:
            trend = "INCREASING 📈"
        elif bpm < prev_bpm:
            trend = "DECREASING 📉"
        else:
            trend = "STABLE ➖"

        print("Trend:", trend)

        if emg_strength >= 3:
            print("⚡ MUSCLE STATE: TENSE (possible seizure/spasm)")
        else:
            print("💤 MUSCLE STATE: RELAXED (possible faint)")

        while True:
            pass

    # =====================================================
    # OUTPUT
    # =====================================================

    print(
        "EMG:", round(emg_strength, 2),
        "BPM:", round(bpm, 1),
        "Accel:", round(accel_mag, 2),
        "Fall:", fall_detected
    )

    prev_bpm = bpm

    pykit_explorer.time.sleep(0.02)
