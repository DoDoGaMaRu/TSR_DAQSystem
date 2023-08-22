from time import time, localtime, strftime


def get_time() -> str:
    return strftime('%H:%M:%S', localtime(time()))


def get_date() -> str:
    return strftime('%Y%m%d', localtime(time()))


def day(time_str: str) -> str:
    return time_str[:-2]


class TimeEvent:
    def __init__(self):
        self.prev = get_time()

    def _update(self):
        self.prev = get_time()

    def is_day_change(self):
        is_day_changed = day(self.prev) != day(get_time())
        if is_day_changed:
            self._update()

        return is_day_changed

    def is_hour_change(self):
        is_hour_changed = self.prev != get_time()
        if is_hour_changed:
            self._update()

        return is_hour_changed
