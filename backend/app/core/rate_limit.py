import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        events = self._events[key]

        while events and now - events[0] > window_seconds:
            events.popleft()

        if len(events) >= max_requests:
            return False

        events.append(now)
        return True


login_rate_limiter = InMemoryRateLimiter()
