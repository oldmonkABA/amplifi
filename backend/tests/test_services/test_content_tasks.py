import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from sqlalchemy import select

from app.models.user import User
from app.models.site import Site
from app.models.content import Content
from app.tasks.content_tasks import (
    find_due_content,
    publish_content_item,
    process_scheduled_content,
)


@pytest.fixture
async def seeded_content(db_session):
    user = User(email="sched@example.com", name="Scheduler", google_id="sched-1")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    # Content due now
    due_content = Content(
        site_id=site.id,
        user_id=user.id,
        platform="twitter",
        content_type="tweet",
        title="Due Tweet",
        body="This should be published now",
        status="scheduled",
        scheduled_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )

    # Content due in the future
    future_content = Content(
        site_id=site.id,
        user_id=user.id,
        platform="twitter",
        content_type="tweet",
        title="Future Tweet",
        body="This is for later",
        status="scheduled",
        scheduled_at=datetime.now(timezone.utc) + timedelta(hours=2),
    )

    # Already published content
    published_content = Content(
        site_id=site.id,
        user_id=user.id,
        platform="twitter",
        content_type="tweet",
        title="Published Tweet",
        body="Already out there",
        status="published",
        scheduled_at=datetime.now(timezone.utc) - timedelta(hours=1),
        published_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )

    # Draft content (not scheduled)
    draft_content = Content(
        site_id=site.id,
        user_id=user.id,
        platform="twitter",
        content_type="tweet",
        title="Draft Tweet",
        body="Not ready yet",
        status="draft",
    )

    db_session.add_all([due_content, future_content, published_content, draft_content])
    await db_session.commit()

    return {
        "user": user,
        "site": site,
        "due": due_content,
        "future": future_content,
        "published": published_content,
        "draft": draft_content,
    }


@pytest.mark.asyncio
async def test_find_due_content(db_session, seeded_content):
    due_items = await find_due_content(db_session)

    assert len(due_items) == 1
    assert due_items[0].title == "Due Tweet"
    assert due_items[0].status == "scheduled"


@pytest.mark.asyncio
async def test_find_due_content_empty(db_session):
    """No scheduled content should return empty list."""
    user = User(email="empty@example.com", name="Empty", google_id="empty-1")
    db_session.add(user)
    await db_session.commit()

    due_items = await find_due_content(db_session)
    assert len(due_items) == 0


@pytest.mark.asyncio
async def test_publish_content_item_success(db_session, seeded_content):
    mock_publisher = AsyncMock()
    mock_publisher.publish.return_value = MagicMock(
        success=True,
        post_id="tweet-999",
        url="https://twitter.com/i/status/tweet-999",
    )

    content = seeded_content["due"]
    result = await publish_content_item(db_session, content, mock_publisher)

    assert result is True
    await db_session.refresh(content)
    assert content.status == "published"
    assert content.published_at is not None
    assert content.platform_post_id == "tweet-999"


@pytest.mark.asyncio
async def test_publish_content_item_failure(db_session, seeded_content):
    mock_publisher = AsyncMock()
    mock_publisher.publish.return_value = MagicMock(
        success=False,
        error="Rate limit exceeded",
        post_id=None,
    )

    content = seeded_content["due"]
    result = await publish_content_item(db_session, content, mock_publisher)

    assert result is False
    await db_session.refresh(content)
    # Content should remain scheduled on failure so it can be retried
    assert content.status == "scheduled"


@pytest.mark.asyncio
async def test_process_scheduled_content(db_session, seeded_content):
    mock_publisher = AsyncMock()
    mock_publisher.publish.return_value = MagicMock(
        success=True,
        post_id="tweet-batch-1",
        url="https://twitter.com/i/status/tweet-batch-1",
    )

    mock_factory = MagicMock()
    mock_factory.create.return_value = mock_publisher

    results = await process_scheduled_content(db_session, mock_factory)

    assert results["processed"] == 1
    assert results["succeeded"] == 1
    assert results["failed"] == 0
