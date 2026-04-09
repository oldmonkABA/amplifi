from dataclasses import dataclass
from datetime import datetime, timezone, timedelta


@dataclass
class PlatformLimits:
    max_requests: int
    window_seconds: int


class RateLimiter:
    def __init__(self):
        self._limits: dict[str, PlatformLimits] = {}
        self._requests: dict[str, list[datetime]] = {}

    def configure(self, platform: str, limits: PlatformLimits):
        self._limits[platform] = limits
        if platform not in self._requests:
            self._requests[platform] = []

    def _clean_old_requests(self, platform: str):
        if platform not in self._limits:
            return
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=self._limits[platform].window_seconds)
        self._requests[platform] = [t for t in self._requests.get(platform, []) if t > cutoff]

    def can_proceed(self, platform: str) -> bool:
        if platform not in self._limits:
            return True
        self._clean_old_requests(platform)
        return len(self._requests.get(platform, [])) < self._limits[platform].max_requests

    def record(self, platform: str):
        if platform not in self._requests:
            self._requests[platform] = []
        self._requests[platform].append(datetime.now(timezone.utc))

    def remaining(self, platform: str) -> int:
        if platform not in self._limits:
            return -1
        self._clean_old_requests(platform)
        return self._limits[platform].max_requests - len(self._requests.get(platform, []))
