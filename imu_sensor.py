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