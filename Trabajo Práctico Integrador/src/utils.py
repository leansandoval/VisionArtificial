import collections
import time

class FPSCounter:
    def __init__(self, window_size=16):
        self.times = collections.deque(maxlen=window_size)

    def tick(self):
        self.times.append(time.time())

    def fps(self):
        if len(self.times) < 2:
            return 0.0
        duration = self.times[-1] - self.times[0]
        if duration == 0:
            return 0.0
        return (len(self.times)-1)/duration
