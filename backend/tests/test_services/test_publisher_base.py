from unittest.mock import AsyncMock

import pytest

from app.services.publishing.base import PlatformPublisher, PublishResult
from app.services.publishing.factory import PublisherFactory


class MockTwitterPublisher(PlatformPublisher):
    """Concrete implementation for testing."""

    platform = "twitter"

    async def publish(self, content_body: str, title: str | None = None, **kwargs) -> PublishResult:
        return PublishResult(
            success=True,
            platform="twitter",
            post_id="tweet-123",
            url="https://twitter.com/user/status/tweet-123",
        )

    async def delete(self, post_id: str) -> bool:
        return True

    async def validate_credentials(self) -> bool:
        return True


class MockLinkedInPublisher(PlatformPublisher):
    """Concrete implementation for testing."""

    platform = "linkedin"

    async def publish(self, content_body: str, title: str | None = None, **kwargs) -> PublishResult:
        return PublishResult(
            success=True,
            platform="linkedin",
            post_id="li-456",
            url="https://linkedin.com/posts/li-456",
        )

    async def delete(self, post_id: str) -> bool:
        return True

    async def validate_credentials(self) -> bool:
        return True


class FailingPublisher(PlatformPublisher):
    """Publisher that simulates a failure."""

    platform = "failing"

    async def publish(self, content_body: str, title: str | None = None, **kwargs) -> PublishResult:
        return PublishResult(
            success=False,
            platform="failing",
            error="API rate limit exceeded",
        )

    async def delete(self, post_id: str) -> bool:
        return False

    async def validate_credentials(self) -> bool:
        return False


def test_publish_result_success():
    result = PublishResult(
        success=True,
        platform="twitter",
        post_id="123",
        url="https://twitter.com/status/123",
    )
    assert result.success is True
    assert result.post_id == "123"
    assert result.error is None


def test_publish_result_failure():
    result = PublishResult(
        success=False,
        platform="twitter",
        error="Authentication failed",
    )
    assert result.success is False
    assert result.post_id is None
    assert result.error == "Authentication failed"


@pytest.mark.asyncio
async def test_mock_publisher_publish():
    publisher = MockTwitterPublisher(credentials={"api_key": "test"})
    result = await publisher.publish("Hello world!")
    assert result.success is True
    assert result.post_id == "tweet-123"
    assert result.platform == "twitter"


@pytest.mark.asyncio
async def test_failing_publisher():
    publisher = FailingPublisher(credentials={})
    result = await publisher.publish("This will fail")
    assert result.success is False
    assert "rate limit" in result.error.lower()


@pytest.mark.asyncio
async def test_publisher_validate_credentials():
    publisher = MockTwitterPublisher(credentials={"api_key": "test"})
    assert await publisher.validate_credentials() is True

    failing = FailingPublisher(credentials={})
    assert await failing.validate_credentials() is False


def test_publisher_factory_register_and_create():
    factory = PublisherFactory()
    factory.register("twitter", MockTwitterPublisher)
    factory.register("linkedin", MockLinkedInPublisher)

    publisher = factory.create("twitter", credentials={"api_key": "test"})
    assert isinstance(publisher, MockTwitterPublisher)
    assert publisher.platform == "twitter"


def test_publisher_factory_unknown_platform():
    factory = PublisherFactory()
    with pytest.raises(ValueError, match="No publisher registered for platform"):
        factory.create("unknown", credentials={})


def test_publisher_factory_list_platforms():
    factory = PublisherFactory()
    factory.register("twitter", MockTwitterPublisher)
    factory.register("linkedin", MockLinkedInPublisher)

    platforms = factory.list_platforms()
    assert "twitter" in platforms
    assert "linkedin" in platforms
    assert len(platforms) == 2
