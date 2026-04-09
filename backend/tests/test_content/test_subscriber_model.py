import pytest
from sqlalchemy import select

from app.models.user import User
from app.models.site import Site
from app.models.subscriber import Subscriber


@pytest.mark.asyncio
async def test_create_subscriber(db_session):
    user = User(email="sub@example.com", name="Sub User", google_id="sub-1")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    subscriber = Subscriber(
        site_id=site.id,
        email="reader@example.com",
        source="landing_page",
        is_active=True,
        drip_status="not_started",
    )
    db_session.add(subscriber)
    await db_session.commit()

    result = await db_session.execute(
        select(Subscriber).where(Subscriber.email == "reader@example.com")
    )
    saved = result.scalar_one()
    assert saved.site_id == site.id
    assert saved.source == "landing_page"
    assert saved.is_active is True
    assert saved.drip_status == "not_started"
    assert saved.tags is None


@pytest.mark.asyncio
async def test_subscriber_with_tags(db_session):
    user = User(email="sub2@example.com", name="Sub2 User", google_id="sub-2")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    subscriber = Subscriber(
        site_id=site.id,
        email="tagged@example.com",
        source="blog_signup",
        is_active=True,
        drip_status="active",
        tags=["early_adopter", "premium"],
    )
    db_session.add(subscriber)
    await db_session.commit()

    result = await db_session.execute(
        select(Subscriber).where(Subscriber.email == "tagged@example.com")
    )
    saved = result.scalar_one()
    assert saved.tags == ["early_adopter", "premium"]
    assert saved.drip_status == "active"


@pytest.mark.asyncio
async def test_subscriber_unsubscribe(db_session):
    user = User(email="sub3@example.com", name="Sub3 User", google_id="sub-3")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    subscriber = Subscriber(
        site_id=site.id,
        email="unsub@example.com",
        source="referral",
        is_active=False,
        drip_status="completed",
        unsubscribe_reason="too_frequent",
    )
    db_session.add(subscriber)
    await db_session.commit()

    result = await db_session.execute(
        select(Subscriber).where(Subscriber.email == "unsub@example.com")
    )
    saved = result.scalar_one()
    assert saved.is_active is False
    assert saved.unsubscribe_reason == "too_frequent"
