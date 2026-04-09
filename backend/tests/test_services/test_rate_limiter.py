import pytest
from datetime import datetime, timezone, timedelta

from app.services.rate_limiter import RateLimiter, PlatformLimits


def test_rate_limiter_allows_within_limit():
    limiter = RateLimiter()
    limiter.configure("twitter", PlatformLimits(max_requests=10, window_seconds=3600))
    assert limiter.can_proceed("twitter") is True


def test_rate_limiter_blocks_at_limit():
    limiter = RateLimiter()
    limiter.configure("twitter", PlatformLimits(max_requests=2, window_seconds=3600))
    limiter.record("twitter")
    limiter.record("twitter")
    assert limiter.can_proceed("twitter") is False


def test_rate_limiter_allows_after_window():
    limiter = RateLimiter()
    limiter.configure("twitter", PlatformLimits(max_requests=1, window_seconds=1))
    past = datetime.now(timezone.utc) - timedelta(seconds=2)
    limiter._requests["twitter"] = [past]
    assert limiter.can_proceed("twitter") is True


def test_rate_limiter_remaining():
    limiter = RateLimiter()
    limiter.configure("twitter", PlatformLimits(max_requests=5, window_seconds=3600))
    limiter.record("twitter")
    limiter.record("twitter")
    assert limiter.remaining("twitter") == 3


def test_rate_limiter_unknown_platform():
    limiter = RateLimiter()
    assert limiter.can_proceed("unknown") is True
    assert limiter.remaining("unknown") == -1
