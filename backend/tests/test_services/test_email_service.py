import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select

from app.models.user import User
from app.models.site import Site
from app.models.subscriber import Subscriber
from app.models.email_campaign import EmailCampaign
from app.services.email_service import EmailService


@pytest.fixture
async def seeded_data(db_session):
    user = User(email="email@example.com", name="Email User", google_id="em-1")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    return {"user": user, "site": site}


@pytest.fixture
def email_service():
    mock_llm = AsyncMock()
    return EmailService(llm=mock_llm)


@pytest.mark.asyncio
async def test_add_subscriber(email_service, db_session, seeded_data):
    site = seeded_data["site"]

    subscriber = await email_service.add_subscriber(
        db=db_session,
        site_id=site.id,
        email="new@reader.com",
        source="landing_page",
        tags=["early_adopter"],
    )

    assert subscriber.email == "new@reader.com"
    assert subscriber.site_id == site.id
    assert subscriber.is_active is True
    assert subscriber.source == "landing_page"
    assert subscriber.tags == ["early_adopter"]


@pytest.mark.asyncio
async def test_add_subscriber_duplicate(email_service, db_session, seeded_data):
    site = seeded_data["site"]

    await email_service.add_subscriber(
        db=db_session, site_id=site.id, email="dup@reader.com", source="blog"
    )

    # Adding same email for same site should return existing subscriber
    subscriber = await email_service.add_subscriber(
        db=db_session, site_id=site.id, email="dup@reader.com", source="referral"
    )

    assert subscriber.email == "dup@reader.com"
    # Source should NOT be overwritten
    assert subscriber.source == "blog"


@pytest.mark.asyncio
async def test_unsubscribe(email_service, db_session, seeded_data):
    site = seeded_data["site"]

    subscriber = await email_service.add_subscriber(
        db=db_session, site_id=site.id, email="unsub@reader.com"
    )

    result = await email_service.unsubscribe(
        db=db_session,
        site_id=site.id,
        email="unsub@reader.com",
        reason="too_frequent",
    )

    assert result is True
    await db_session.refresh(subscriber)
    assert subscriber.is_active is False
    assert subscriber.unsubscribe_reason == "too_frequent"


@pytest.mark.asyncio
async def test_unsubscribe_nonexistent(email_service, db_session, seeded_data):
    site = seeded_data["site"]
    result = await email_service.unsubscribe(
        db=db_session,
        site_id=site.id,
        email="nonexistent@reader.com",
    )
    assert result is False


@pytest.mark.asyncio
async def test_list_subscribers(email_service, db_session, seeded_data):
    site = seeded_data["site"]

    for i in range(5):
        await email_service.add_subscriber(
            db=db_session, site_id=site.id, email=f"list{i}@reader.com"
        )

    # Unsubscribe one
    await email_service.unsubscribe(
        db=db_session, site_id=site.id, email="list2@reader.com"
    )

    active = await email_service.list_subscribers(
        db=db_session, site_id=site.id, active_only=True
    )
    assert len(active) == 4

    all_subs = await email_service.list_subscribers(
        db=db_session, site_id=site.id, active_only=False
    )
    assert len(all_subs) == 5


@pytest.mark.asyncio
async def test_create_campaign(email_service, db_session, seeded_data):
    user = seeded_data["user"]
    site = seeded_data["site"]

    campaign = await email_service.create_campaign(
        db=db_session,
        site_id=site.id,
        user_id=user.id,
        subject="Welcome!",
        body="<h1>Welcome to our newsletter</h1>",
        campaign_type="one_off",
        audience_segment={"tags": ["early_adopter"]},
    )

    assert campaign.subject == "Welcome!"
    assert campaign.status == "draft"
    assert campaign.campaign_type == "one_off"
    assert campaign.audience_segment == {"tags": ["early_adopter"]}


@pytest.mark.asyncio
async def test_generate_campaign_content(email_service, db_session, seeded_data):
    email_service.llm.generate.return_value = """Subject: 5 AI Marketing Trends You Cannot Ignore in 2026

<h1>5 AI Marketing Trends You Cannot Ignore</h1>

<p>Hi there,</p>

<p>The marketing landscape is evolving rapidly. Here are the top 5 trends...</p>

<ol>
<li>Automated content generation across platforms</li>
<li>AI-powered SEO optimization</li>
<li>Smart scheduling based on audience behavior</li>
<li>Cross-platform content repurposing</li>
<li>Predictive engagement analytics</li>
</ol>

<p>Stay ahead of the curve!</p>"""

    result = await email_service.generate_campaign_content(
        topic="AI marketing trends for 2026",
        site_name="Amplifi",
        tone="professional",
    )

    assert "subject" in result
    assert "body" in result
    assert len(result["body"]) > 50


@pytest.mark.asyncio
async def test_get_subscriber_count(email_service, db_session, seeded_data):
    site = seeded_data["site"]

    for i in range(3):
        await email_service.add_subscriber(
            db=db_session, site_id=site.id, email=f"count{i}@reader.com"
        )

    count = await email_service.get_subscriber_count(db=db_session, site_id=site.id)
    assert count == 3
