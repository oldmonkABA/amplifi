import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models.user import User
from app.models.site import Site
from app.models.content import Content, ContentGroup


@pytest.mark.asyncio
async def test_create_content_group(db_session):
    user = User(email="cg@example.com", name="CG User", google_id="cg-1")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    group = ContentGroup(
        site_id=site.id,
        name="Product Launch Bundle",
        description="Cross-platform content for v2 launch",
    )
    db_session.add(group)
    await db_session.commit()

    result = await db_session.execute(
        select(ContentGroup).where(ContentGroup.name == "Product Launch Bundle")
    )
    saved = result.scalar_one()
    assert saved.site_id == site.id
    assert saved.description == "Cross-platform content for v2 launch"
    assert saved.id is not None
    assert saved.created_at is not None


@pytest.mark.asyncio
async def test_create_content(db_session):
    user = User(email="ct@example.com", name="CT User", google_id="ct-1")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    content = Content(
        site_id=site.id,
        user_id=user.id,
        platform="twitter",
        content_type="tweet",
        title="Launch Tweet",
        body="We just launched v2! Check it out at https://example.com",
        status="draft",
    )
    db_session.add(content)
    await db_session.commit()

    result = await db_session.execute(
        select(Content).where(Content.title == "Launch Tweet")
    )
    saved = result.scalar_one()
    assert saved.platform == "twitter"
    assert saved.content_type == "tweet"
    assert saved.status == "draft"
    assert saved.scheduled_at is None
    assert saved.published_at is None
    assert saved.group_id is None
    assert saved.meta_data is None


@pytest.mark.asyncio
async def test_content_with_group(db_session):
    user = User(email="cg2@example.com", name="CG2 User", google_id="cg-2")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    group = ContentGroup(site_id=site.id, name="Launch Bundle")
    db_session.add(group)
    await db_session.commit()

    content = Content(
        site_id=site.id,
        user_id=user.id,
        platform="linkedin",
        content_type="post",
        title="Launch Post",
        body="Excited to announce our v2 launch!",
        status="draft",
        group_id=group.id,
    )
    db_session.add(content)
    await db_session.commit()

    result = await db_session.execute(
        select(Content).where(Content.group_id == group.id)
    )
    saved = result.scalar_one()
    assert saved.group_id == group.id
    assert saved.platform == "linkedin"


@pytest.mark.asyncio
async def test_content_scheduled(db_session):
    user = User(email="cs@example.com", name="CS User", google_id="cs-1")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    scheduled_time = datetime(2026, 5, 1, 14, 0, 0, tzinfo=timezone.utc)
    content = Content(
        site_id=site.id,
        user_id=user.id,
        platform="twitter",
        content_type="tweet",
        title="Scheduled Tweet",
        body="This is a scheduled tweet",
        status="scheduled",
        scheduled_at=scheduled_time,
        target_timezone="America/New_York",
    )
    db_session.add(content)
    await db_session.commit()

    result = await db_session.execute(
        select(Content).where(Content.status == "scheduled")
    )
    saved = result.scalar_one()
    assert saved.scheduled_at == scheduled_time
    assert saved.target_timezone == "America/New_York"
