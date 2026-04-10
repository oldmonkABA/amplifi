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
        email="router_analytics@test.com",
        name="Router Analytics Tester",
        google_id="google_analytics_router_123",
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


class TestOverviewEndpoint:
    @pytest.mark.asyncio
    async def test_overview_returns_data(
        self, db_session: AsyncSession, user: User, site: Site, service: AnalyticsService
    ):
        db_session.add(Content(
            site_id=site.id, user_id=user.id,
            platform="twitter", content_type="post",
            title="T", body="B", status="published",
        ))
        db_session.add(Subscriber(
            site_id=site.id, email="s@t.com", source="signup", is_active=True,
        ))
        await db_session.commit()

        overview = await service.get_site_overview(db_session, site.id)
        assert overview["total_content"] == 1
        assert overview["total_subscribers"] == 1
        assert overview["active_subscribers"] == 1


class TestContentAnalyticsEndpoint:
    @pytest.mark.asyncio
    async def test_content_analytics(
        self, db_session: AsyncSession, user: User, site: Site, service: AnalyticsService
    ):
        db_session.add(Content(
            site_id=site.id, user_id=user.id,
            platform="blog", content_type="post",
            title="T", body="B", status="draft",
        ))
        await db_session.commit()

        result = await service.get_content_analytics(db_session, site.id)
        assert result["total"] == 1
        assert result["draft_count"] == 1


class TestAdsAnalyticsEndpoint:
    @pytest.mark.asyncio
    async def test_ads_analytics(
        self, db_session: AsyncSession, user: User, site: Site, service: AnalyticsService
    ):
        db_session.add(AdCampaign(
            site_id=site.id, user_id=user.id,
            name="C", platform="google_ads",
            objective="traffic", daily_budget_cents=5000, status="active",
        ))
        await db_session.commit()

        result = await service.get_ads_analytics(db_session, site.id)
        assert result["total_campaigns"] == 1
        assert result["total_budget_cents_daily"] == 5000


class TestEmailAnalyticsEndpoint:
    @pytest.mark.asyncio
    async def test_email_analytics(
        self, db_session: AsyncSession, user: User, site: Site, service: AnalyticsService
    ):
        db_session.add(EmailCampaign(
            site_id=site.id, user_id=user.id,
            subject="S", body="B", campaign_type="one_off", status="sent",
            sent_count=100, open_count=30, click_count=10,
        ))
        await db_session.commit()

        result = await service.get_email_analytics(db_session, site.id)
        assert result["total_sent"] == 100
        assert result["open_rate"] == pytest.approx(0.3, rel=1e-2)


class TestTimeseriesEndpoint:
    @pytest.mark.asyncio
    async def test_timeseries(
        self, db_session: AsyncSession, site: Site, service: AnalyticsService
    ):
        db_session.add(MetricSnapshot(
            site_id=site.id, metric_type="subscriber_count",
            value=100.0,
            recorded_at=datetime(2026, 4, 5, 12, 0, tzinfo=timezone.utc),
        ))
        await db_session.commit()

        points = await service.get_timeseries(
            db_session, site.id, "subscriber_count",
            start=datetime(2026, 4, 1, tzinfo=timezone.utc),
            end=datetime(2026, 4, 10, tzinfo=timezone.utc),
        )
        assert len(points) == 1
        assert points[0]["value"] == 100.0


class TestRecordSnapshot:
    @pytest.mark.asyncio
    async def test_record_snapshot(
        self, db_session: AsyncSession, site: Site, service: AnalyticsService
    ):
        snapshot = await service.record_snapshot(
            db_session, site_id=site.id,
            metric_type="subscriber_count", value=300.0,
        )
        assert snapshot.value == 300.0
        assert snapshot.site_id == site.id
