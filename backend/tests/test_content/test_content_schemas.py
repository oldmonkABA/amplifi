from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.content.schemas import (
    ContentCreateRequest,
    ContentUpdateRequest,
    ContentResponse,
    ContentGroupCreateRequest,
    ContentGenerateRequest,
)


def test_content_create_request_valid():
    req = ContentCreateRequest(
        site_id="550e8400-e29b-41d4-a716-446655440000",
        platform="twitter",
        content_type="tweet",
        title="My Tweet",
        body="Hello world!",
    )
    assert req.platform == "twitter"
    assert req.status == "draft"


def test_content_create_request_invalid_platform():
    with pytest.raises(ValidationError) as exc_info:
        ContentCreateRequest(
            site_id="550e8400-e29b-41d4-a716-446655440000",
            platform="tiktok",
            content_type="video",
            title="My Video",
            body="Hello world!",
        )
    assert "platform" in str(exc_info.value).lower()


def test_content_create_request_with_schedule():
    scheduled = datetime(2026, 5, 1, 14, 0, 0, tzinfo=timezone.utc)
    req = ContentCreateRequest(
        site_id="550e8400-e29b-41d4-a716-446655440000",
        platform="linkedin",
        content_type="post",
        title="Scheduled Post",
        body="Coming soon!",
        scheduled_at=scheduled,
        target_timezone="America/New_York",
    )
    assert req.scheduled_at == scheduled
    assert req.target_timezone == "America/New_York"


def test_content_update_request_partial():
    req = ContentUpdateRequest(body="Updated body text")
    assert req.body == "Updated body text"
    assert req.title is None
    assert req.status is None


def test_content_update_status_only():
    req = ContentUpdateRequest(status="approved")
    assert req.status == "approved"


def test_content_update_invalid_status():
    with pytest.raises(ValidationError):
        ContentUpdateRequest(status="invalid_status")


def test_content_response_from_attributes():
    resp = ContentResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        site_id="550e8400-e29b-41d4-a716-446655440001",
        user_id="550e8400-e29b-41d4-a716-446655440002",
        platform="twitter",
        content_type="tweet",
        title="My Tweet",
        body="Hello!",
        status="draft",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert resp.platform == "twitter"


def test_content_group_create():
    req = ContentGroupCreateRequest(
        site_id="550e8400-e29b-41d4-a716-446655440000",
        name="Launch Bundle",
        description="Cross-platform launch content",
    )
    assert req.name == "Launch Bundle"


def test_content_generate_request():
    req = ContentGenerateRequest(
        site_id="550e8400-e29b-41d4-a716-446655440000",
        platform="twitter",
        content_type="tweet",
        topic="Product launch announcement",
        tone="professional",
        keywords=["ai", "marketing", "automation"],
    )
    assert req.platform == "twitter"
    assert req.tone == "professional"
    assert len(req.keywords) == 3


def test_content_generate_request_defaults():
    req = ContentGenerateRequest(
        site_id="550e8400-e29b-41d4-a716-446655440000",
        platform="blog",
        content_type="article",
        topic="SEO best practices",
    )
    assert req.tone == "professional"
    assert req.keywords == []
