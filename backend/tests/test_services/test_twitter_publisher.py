from unittest.mock import AsyncMock, patch, MagicMock
import json

import pytest

from app.services.publishing.twitter import TwitterPublisher
from app.services.publishing.base import PublishResult


@pytest.fixture
def credentials():
    return {
        "api_key": "test-api-key",
        "api_secret": "test-api-secret",
        "access_token": "test-access-token",
        "access_token_secret": "test-access-token-secret",
        "bearer_token": "test-bearer-token",
    }


@pytest.fixture
def publisher(credentials):
    return TwitterPublisher(credentials=credentials)


def test_twitter_publisher_platform(publisher):
    assert publisher.platform == "twitter"


def test_twitter_publisher_stores_credentials(publisher, credentials):
    assert publisher.credentials == credentials


@pytest.mark.asyncio
async def test_publish_tweet_success(publisher):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "data": {
            "id": "1234567890",
            "text": "Hello world!",
        }
    }

    with patch("app.services.publishing.twitter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await publisher.publish("Hello world!")

    assert result.success is True
    assert result.post_id == "1234567890"
    assert result.platform == "twitter"
    assert "twitter.com" in result.url


@pytest.mark.asyncio
async def test_publish_tweet_failure(publisher):
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = '{"detail": "Forbidden: rate limit exceeded"}'
    mock_response.json.return_value = {"detail": "Forbidden: rate limit exceeded"}

    with patch("app.services.publishing.twitter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await publisher.publish("This will fail")

    assert result.success is False
    assert result.error is not None


@pytest.mark.asyncio
async def test_publish_tweet_network_error(publisher):
    with patch("app.services.publishing.twitter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.side_effect = Exception("Connection refused")
        mock_client_cls.return_value = mock_client

        result = await publisher.publish("Network error tweet")

    assert result.success is False
    assert "Connection refused" in result.error


@pytest.mark.asyncio
async def test_delete_tweet_success(publisher):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"deleted": True}}

    with patch("app.services.publishing.twitter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.delete.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await publisher.delete("1234567890")

    assert result is True


@pytest.mark.asyncio
async def test_delete_tweet_failure(publisher):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not found"

    with patch("app.services.publishing.twitter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.delete.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await publisher.delete("nonexistent")

    assert result is False


@pytest.mark.asyncio
async def test_validate_credentials_success(publisher):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"id": "123", "name": "Test User"}}

    with patch("app.services.publishing.twitter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await publisher.validate_credentials()

    assert result is True


@pytest.mark.asyncio
async def test_validate_credentials_failure(publisher):
    mock_response = MagicMock()
    mock_response.status_code = 401

    with patch("app.services.publishing.twitter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await publisher.validate_credentials()

    assert result is False


def test_twitter_publisher_builds_oauth_header(publisher):
    """Verify the publisher can construct an auth header."""
    header = publisher._build_auth_header()
    assert "Bearer" in header or "OAuth" in header
