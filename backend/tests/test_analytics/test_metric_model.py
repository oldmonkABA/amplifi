import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.site import Site
from app.models.metric import MetricSnapshot, METRIC_TYPES


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    user = User(
        email="analytics@test.com",
        name="Analytics Tester",
        google_id="google_analytics_123",
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


class TestMetricSnapshotModel:
    @pytest.mark.asyncio
    async def test_create_snapshot(self, db_session: AsyncSession, site: Site):
        snapshot = MetricSnapshot(
            site_id=site.id,
            metric_type="subscriber_count",
            value=150.0,
            recorded_at=datetime(2026, 4, 10, 12, 0, tzinfo=timezone.utc),
        )
        db_session.add(snapshot)
        await db_session.commit()
        await db_session.refresh(snapshot)

        assert snapshot.id is not None
        assert snapshot.site_id == site.id
        assert snapshot.metric_type == "subscriber_count"
        assert snapshot.value == 150.0
        assert snapshot.dimensions is None

    @pytest.mark.asyncio
    async def test_snapshot_with_dimensions(self, db_session: AsyncSession, site: Site):
        snapshot = MetricSnapshot(
            site_id=site.id,
            metric_type="content_published",
            value=5.0,
            dimensions={"platform": "twitter"},
            recorded_at=datetime(2026, 4, 10, 12, 0, tzinfo=timezone.utc),
        )
        db_session.add(snapshot)
        await db_session.commit()
        await db_session.refresh(snapshot)

        assert snapshot.dimensions == {"platform": "twitter"}

    @pytest.mark.asyncio
    async def test_query_snapshots_by_site_and_type(self, db_session: AsyncSession, site: Site):
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

        result = await db_session.execute(
            select(MetricSnapshot)
            .where(MetricSnapshot.site_id == site.id)
            .where(MetricSnapshot.metric_type == "subscriber_count")
            .order_by(MetricSnapshot.recorded_at)
        )
        snapshots = result.scalars().all()
        assert len(snapshots) == 5
        assert snapshots[0].value == 100.0
        assert snapshots[4].value == 140.0

    @pytest.mark.asyncio
    async def test_metric_types_constant(self):
        assert "subscriber_count" in METRIC_TYPES
        assert "content_published" in METRIC_TYPES
        assert "ad_spend" in METRIC_TYPES
        assert "email_sent" in METRIC_TYPES
        assert "email_opened" in METRIC_TYPES
        assert "email_clicked" in METRIC_TYPES
