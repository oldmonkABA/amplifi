import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.site import Site
from app.models.content import Content
from app.models.ad import AdCampaign, Ad
from app.models.subscriber import Subscriber
from app.models.email_campaign import EmailCampaign
from app.models.metric import MetricSnapshot
from app.services.analytics_service import AnalyticsService


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    user = User(
        email="svc@test.com",
        name="Service Tester",
        google_id="google_svc_123",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def site(db_session: AsyncSession, user: User) -> Site:
    site = Site(
        user_id=user.id,
        url="https://example.com",
        name="Test Site",
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site


@pytest.fixture
def service():
    return AnalyticsService()


class TestSiteOverview:
    @pytest.mark.asyncio
    async def test_empty_site_overview(
        self, db_session: AsyncSession, site: Site, service: AnalyticsService
    ):
        overview = await service.get_site_overview(db_session, site.id)
        assert overview["total_content"] == 0
        assert overview["total_campaigns"] == 0
        assert overview["total_ads"] == 0
        assert overview["total_subscribers"] == 0
        assert overview["active_subscribers"] == 0
        assert overview["content_by_status"] == []
        assert overview["content_by_platform"] == []

    @pytest.mark.asyncio
    async def test_site_overview_with_data(
        self, db_session: AsyncSession, user: User, site: Site, service: AnalyticsService
    ):
        for platform, status in [
            ("twitter", "published"), ("twitter", "draft"),
            ("blog", "published"), ("blog", "scheduled"),
            ("linkedin", "published"),
        ]:
            db_session.add(Content(
                site_id=site.id, user_id=user.id,
                platform=platform, content_type="post",
                title="Test", body="Body", status=status,
            ))

        campaign = AdCampaign(
            site_id=site.id, user_id=user.id,
            name="C1", platform="google_ads",
            objective="traffic", daily_budget_cents=5000, status="active",
        )
        db_session.add(campaign)
        await db_session.flush()
        db_session.add(Ad(
            campaign_id=campaign.id, headline="H", description="D",
            final_url="https://example.com", status="active",
        ))
        db_session.add(Ad(
            campaign_id=campaign.id, headline="H2", description="D2",
            final_url="https://example.com", status="draft",
        ))

        db_session.add(Subscriber(
            site_id=site.id, email="a@t.com", source="signup", is_active=True,
        ))
        db_session.add(Subscriber(
            site_id=site.id, email="b@t.com", source="signup", is_active=True,
        ))
        db_session.add(Subscriber(
            site_id=site.id, email="c@t.com", source="signup", is_active=False,
        ))

        await db_session.commit()

        overview = await service.get_site_overview(db_session, site.id)
        assert overview["total_content"] == 5
        assert overview["total_campaigns"] == 1
        assert overview["total_ads"] == 2
        assert overview["total_subscribers"] == 3
        assert overview["active_subscribers"] == 2

        published = next(
            (s for s in overview["content_by_status"] if s["status"] == "published"), None
        )
        assert published is not None
        assert published["count"] == 3

        twitter = next(
            (p for p in overview["content_by_platform"] if p["platform"] == "twitter"), None
        )
        assert twitter is not None
        assert twitter["count"] == 2


class TestContentAnalytics:
    @pytest.mark.asyncio
    async def test_content_analytics(
        self, db_session: AsyncSession, user: User, site: Site, service: AnalyticsService
    ):
        for platform, status in [
            ("twitter", "published"), ("twitter", "published"),
            ("blog", "draft"), ("blog", "scheduled"),
            ("linkedin", "published"),
        ]:
            db_session.add(Content(
                site_id=site.id, user_id=user.id,
                platform=platform, content_type="post",
                title="T", body="B", status=status,
            ))
        await db_session.commit()

        result = await service.get_content_analytics(db_session, site.id)
        assert result["total"] == 5
        assert result["published_count"] == 3
        assert result["scheduled_count"] == 1
        assert result["draft_count"] == 1


class TestAdsAnalytics:
    @pytest.mark.asyncio
    async def test_ads_analytics(
        self, db_session: AsyncSession, user: User, site: Site, service: AnalyticsService
    ):
        c1 = AdCampaign(
            site_id=site.id, user_id=user.id,
            name="C1", platform="google_ads",
            objective="traffic", daily_budget_cents=5000, status="active",
        )
        c2 = AdCampaign(
            site_id=site.id, user_id=user.id,
            name="C2", platform="facebook_ads",
            objective="awareness", daily_budget_cents=3000, status="draft",
        )
        db_session.add_all([c1, c2])
        await db_session.flush()

        db_session.add(Ad(
            campaign_id=c1.id, headline="H", description="D",
            final_url="https://example.com", status="active",
        ))
        db_session.add(Ad(
            campaign_id=c1.id, headline="H2", description="D2",
            final_url="https://example.com", status="draft",
        ))
        db_session.add(Ad(
            campaign_id=c2.id, headline="H3", description="D3",
            final_url="https://example.com", status="draft",
        ))
        await db_session.commit()

        result = await service.get_ads_analytics(db_session, site.id)
        assert result["total_campaigns"] == 2
        assert result["total_ads"] == 3
        assert result["total_budget_cents_daily"] == 8000

        active_campaigns = next(
            (s for s in result["campaigns_by_status"] if s["status"] == "active"), None
        )
        assert active_campaigns is not None
        assert active_campaigns["count"] == 1


class TestEmailAnalytics:
    @pytest.mark.asyncio
    async def test_email_analytics(
        self, db_session: AsyncSession, user: User, site: Site, service: AnalyticsService
    ):
        db_session.add(EmailCampaign(
            site_id=site.id, user_id=user.id,
            subject="S1", body="B1", campaign_type="one_off", status="sent",
            sent_count=100, open_count=40, click_count=15,
        ))
        db_session.add(EmailCampaign(
            site_id=site.id, user_id=user.id,
            subject="S2", body="B2", campaign_type="digest", status="sent",
            sent_count=200, open_count=60, click_count=25,
        ))
        db_session.add(Subscriber(
            site_id=site.id, email="a@t.com", source="signup", is_active=True,
        ))
        db_session.add(Subscriber(
            site_id=site.id, email="b@t.com", source="signup", is_active=False,
        ))
        await db_session.commit()

        result = await service.get_email_analytics(db_session, site.id)
        assert result["total_campaigns"] == 2
        assert result["total_sent"] == 300
        assert result["total_opened"] == 100
        assert result["total_clicked"] == 40
        assert result["open_rate"] == pytest.approx(100 / 300, rel=1e-2)
        assert result["click_rate"] == pytest.approx(40 / 300, rel=1e-2)
        assert result["total_subscribers"] == 2
        assert result["active_subscribers"] == 1

    @pytest.mark.asyncio
    async def test_email_analytics_no_sends(
        self, db_session: AsyncSession, site: Site, service: AnalyticsService
    ):
        result = await service.get_email_analytics(db_session, site.id)
        assert result["open_rate"] == 0.0
        assert result["click_rate"] == 0.0


class TestTimeseries:
    @pytest.mark.asyncio
    async def test_get_timeseries(
        self, db_session: AsyncSession, site: Site, service: AnalyticsService
    ):
        for i in range(5):
            db_session.add(MetricSnapshot(
                site_id=site.id,
                metric_type="subscriber_count",
                value=100.0 + i * 10,
                recorded_at=datetime(2026, 4, i + 1, 12, 0, tzinfo=timezone.utc),
            ))
        db_session.add(MetricSnapshot(
            site_id=site.id,
            metric_type="content_published",
            value=3.0,
            recorded_at=datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc),
        ))
        await db_session.commit()

        points = await service.get_timeseries(
            db_session, site.id, "subscriber_count",
            start=datetime(2026, 4, 1, tzinfo=timezone.utc),
            end=datetime(2026, 4, 6, tzinfo=timezone.utc),
        )
        assert len(points) == 5
        assert points[0]["value"] == 100.0
        assert points[4]["value"] == 140.0

    @pytest.mark.asyncio
    async def test_record_snapshot(
        self, db_session: AsyncSession, site: Site, service: AnalyticsService
    ):
        snapshot = await service.record_snapshot(
            db_session,
            site_id=site.id,
            metric_type="subscriber_count",
            value=250.0,
        )
        assert snapshot.value == 250.0
        assert snapshot.metric_type == "subscriber_count"
