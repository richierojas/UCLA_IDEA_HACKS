class EMGProcessor:
    def __init__(self):
        self.filtered = 0
        self.alpha = 0.2

    def process(self, envelope_value):
        self.filtered = (1 - self.alpha) * self.filtered + self.alpha * envelope_value

        activation = self.filtered / 50000
        activation = max(0, min(1, activation))

        return activation