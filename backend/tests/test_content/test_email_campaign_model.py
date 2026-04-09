from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models.user import User
from app.models.site import Site
from app.models.email_campaign import EmailCampaign


@pytest.mark.asyncio
async def test_create_email_campaign(db_session):
    user = User(email="ec@example.com", name="EC User", google_id="ec-1")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    campaign = EmailCampaign(
        site_id=site.id,
        user_id=user.id,
        subject="Welcome to our newsletter!",
        body="<h1>Welcome!</h1><p>Thanks for subscribing.</p>",
        campaign_type="drip",
        status="draft",
        audience_segment={"tags": ["early_adopter"]},
    )
    db_session.add(campaign)
    await db_session.commit()

    result = await db_session.execute(
        select(EmailCampaign).where(EmailCampaign.subject == "Welcome to our newsletter!")
    )
    saved = result.scalar_one()
    assert saved.site_id == site.id
    assert saved.campaign_type == "drip"
    assert saved.status == "draft"
    assert saved.audience_segment == {"tags": ["early_adopter"]}
    assert saved.sent_at is None
    assert saved.sent_count is None
    assert saved.open_count is None


@pytest.mark.asyncio
async def test_email_campaign_with_schedule(db_session):
    user = User(email="ec2@example.com", name="EC2 User", google_id="ec-2")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    send_time = datetime(2026, 5, 15, 9, 0, 0, tzinfo=timezone.utc)
    campaign = EmailCampaign(
        site_id=site.id,
        user_id=user.id,
        subject="Weekly Digest",
        body="<p>Here is your weekly digest.</p>",
        campaign_type="digest",
        status="scheduled",
        scheduled_at=send_time,
    )
    db_session.add(campaign)
    await db_session.commit()

    result = await db_session.execute(
        select(EmailCampaign).where(EmailCampaign.status == "scheduled")
    )
    saved = result.scalar_one()
    assert saved.scheduled_at == send_time
    assert saved.campaign_type == "digest"


@pytest.mark.asyncio
async def test_email_campaign_sent_stats(db_session):
    user = User(email="ec3@example.com", name="EC3 User", google_id="ec-3")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    sent_time = datetime(2026, 4, 1, 10, 0, 0, tzinfo=timezone.utc)
    campaign = EmailCampaign(
        site_id=site.id,
        user_id=user.id,
        subject="April Newsletter",
        body="<p>April updates.</p>",
        campaign_type="one_off",
        status="sent",
        sent_at=sent_time,
        sent_count=1500,
        open_count=450,
        click_count=120,
    )
    db_session.add(campaign)
    await db_session.commit()

    result = await db_session.execute(
        select(EmailCampaign).where(EmailCampaign.status == "sent")
    )
    saved = result.scalar_one()
    assert saved.sent_count == 1500
    assert saved.open_count == 450
    assert saved.click_count == 120
