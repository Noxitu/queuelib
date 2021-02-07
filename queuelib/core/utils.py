import sys
import time


class measure_time:
    def __init__(self):
        self._start = time.time()

    def get(self):
        return time.time() - self._start

    def smart_round(self):
        duration = self.get()

        if duration < 0.3:
            return f'{int(duration*100)}ms'
        
        if duration < 3:
            return f'{duration:.1f}s'

        duration = int(duration)

        if duration < 60:
            return f'{duration}s'

        m, s = duration // 60, duration % 60

        if m < 10:
            return f'{m}m {s}s'

        if m < 60:
            return f'{m}m'

        h, m = m // 60, s % 60

        if h < 10:
            return f'{h}h {m}m'

        return f'{h}h'


def message(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)
