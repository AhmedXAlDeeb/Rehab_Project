from collections import defaultdict
from threading import Lock


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self.counters = defaultdict(float)
        self.gauges = defaultdict(float)

    def inc(self, key: str, val: float = 1.0) -> None:
        with self._lock:
            self.counters[key] += val

    def set_gauge(self, key: str, val: float) -> None:
        with self._lock:
            self.gauges[key] = val

    def render_prometheus(self) -> str:
        with self._lock:
            lines: list[str] = []
            for key, val in self.counters.items():
                lines.append(f"# TYPE {key} counter")
                lines.append(f"{key} {val}")
            for key, val in self.gauges.items():
                lines.append(f"# TYPE {key} gauge")
                lines.append(f"{key} {val}")
            return "\n".join(lines) + "\n"


metrics = MetricsRegistry()
