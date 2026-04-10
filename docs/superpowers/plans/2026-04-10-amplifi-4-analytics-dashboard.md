# Analytics & Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add analytics API endpoints that aggregate data from existing Content, Ad, Email, and Subscriber models into dashboard-ready responses, plus a MetricSnapshot model for time-series tracking.

**Architecture:** A new `analytics` module with a router + schemas + service layer. The service performs aggregation queries over existing models (no new data sources needed). A `MetricSnapshot` model stores periodic snapshots for time-series graphs (subscriber growth, publishing velocity, etc.). All endpoints are read-only except snapshot recording.

**Tech Stack:** FastAPI, SQLAlchemy async, Pydantic v2, pytest + pytest-asyncio, existing models

---

## File Structure

### New Files

| File | Responsibility |
|------|---------------|
| `backend/app/models/metric.py` | MetricSnapshot SQLAlchemy model |
| `backend/app/modules/analytics/__init__.py` | Package init |
| `backend/app/modules/analytics/router.py` | All analytics API endpoints |
| `backend/app/modules/analytics/schemas.py` | Pydantic response schemas |
| `backend/app/services/analytics_service.py` | Aggregation query logic |
| `backend/tests/test_analytics/__init__.py` | Test package init |
| `backend/tests/test_analytics/test_metric_model.py` | MetricSnapshot model tests |
| `backend/tests/test_analytics/test_analytics_schemas.py` | Schema validation tests |
| `backend/tests/test_analytics/test_analytics_service.py` | Service aggregation tests |
| `backend/tests/test_analytics/test_analytics_router.py` | Router/endpoint tests |

### Modified Files

| File | Change |
|------|--------|
| `backend/app/models/__init__.py` | Add MetricSnapshot import |
| `backend/app/main.py` | Include analytics router |

---

### Task 1: MetricSnapshot Model

**Files:**
- Create: `backend/app/models/metric.py`
- Create: `backend/tests/test_analytics/__init__.py`
- Create: `backend/tests/test_analytics/test_metric_model.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Create test package and write model tests**

Create `backend/tests/test_analytics/__init__.py` (empty file).

Create `backend/tests/test_analytics/test_metric_model.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_analytics/test_metric_model.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.models.metric'`

- [ ] **Step 3: Create the MetricSnapshot model**

Create `backend/app/models/metric.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin


METRIC_TYPES = [
    "subscriber_count",
    "content_published",
    "content_scheduled",
    "ad_spend",
    "ad_impressions",
    "ad_clicks",
    "email_sent",
    "email_opened",
    "email_clicked",
]


class MetricSnapshot(Base, UUIDMixin):
    __tablename__ = "metric_snapshots"

    site_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sites.id"), nullable=False, index=True
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    dimensions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
```

- [ ] **Step 4: Register model in `__init__.py`**

Add to `backend/app/models/__init__.py`:

```python
from app.models.metric import MetricSnapshot
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_analytics/test_metric_model.py -v`
Expected: All 4 tests PASS

- [ ] **Step 6: Run full test suite for regression**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest -v`
Expected: All 167 existing + 4 new = 171 PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/metric.py backend/app/models/__init__.py backend/tests/test_analytics/
git commit -m "feat(analytics): add MetricSnapshot model for time-series tracking"
```

---

### Task 2: Analytics Schemas

**Files:**
- Create: `backend/app/modules/analytics/__init__.py`
- Create: `backend/app/modules/analytics/schemas.py`
- Create: `backend/tests/test_analytics/test_analytics_schemas.py`

- [ ] **Step 1: Write schema validation tests**

Create `backend/tests/test_analytics/test_analytics_schemas.py`:

```python
from datetime import datetime, timezone

import pytest

from app.modules.analytics.schemas import (
    SiteOverviewResponse,
    ContentAnalyticsResponse,
    AdsAnalyticsResponse,
    EmailAnalyticsResponse,
    TimeseriesPoint,
    TimeseriesResponse,
    MetricSnapshotCreateRequest,
    PlatformCount,
    StatusCount,
)


class TestSiteOverviewResponse:
    def test_valid_overview(self):
        resp = SiteOverviewResponse(
            site_id="550e8400-e29b-41d4-a716-446655440000",
            total_content=42,
            content_by_status=[
                StatusCount(status="published", count=20),
                StatusCount(status="draft", count=22),
            ],
            content_by_platform=[
                PlatformCount(platform="twitter", count=30),
                PlatformCount(platform="blog", count=12),
            ],
            total_campaigns=5,
            total_ads=15,
            total_subscribers=200,
            active_subscribers=180,
        )
        assert resp.total_content == 42
        assert len(resp.content_by_status) == 2
        assert resp.active_subscribers == 180


class TestContentAnalyticsResponse:
    def test_valid_content_analytics(self):
        resp = ContentAnalyticsResponse(
            site_id="550e8400-e29b-41d4-a716-446655440000",
            total=50,
            by_status=[StatusCount(status="published", count=30)],
            by_platform=[PlatformCount(platform="twitter", count=25)],
            published_count=30,
            scheduled_count=10,
            draft_count=10,
        )
        assert resp.published_count == 30


class TestAdsAnalyticsResponse:
    def test_valid_ads_analytics(self):
        resp = AdsAnalyticsResponse(
            site_id="550e8400-e29b-41d4-a716-446655440000",
            total_campaigns=3,
            campaigns_by_status=[StatusCount(status="active", count=2)],
            campaigns_by_platform=[PlatformCount(platform="google_ads", count=2)],
            total_ads=10,
            ads_by_status=[StatusCount(status="draft", count=5)],
            total_budget_cents_daily=15000,
        )
        assert resp.total_budget_cents_daily == 15000


class TestEmailAnalyticsResponse:
    def test_valid_email_analytics(self):
        resp = EmailAnalyticsResponse(
            site_id="550e8400-e29b-41d4-a716-446655440000",
            total_campaigns=4,
            total_sent=1000,
            total_opened=350,
            total_clicked=120,
            open_rate=0.35,
            click_rate=0.12,
            total_subscribers=500,
            active_subscribers=450,
        )
        assert resp.open_rate == 0.35
        assert resp.click_rate == 0.12


class TestTimeseriesResponse:
    def test_valid_timeseries(self):
        resp = TimeseriesResponse(
            site_id="550e8400-e29b-41d4-a716-446655440000",
            metric_type="subscriber_count",
            points=[
                TimeseriesPoint(
                    recorded_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
                    value=100.0,
                ),
                TimeseriesPoint(
                    recorded_at=datetime(2026, 4, 2, tzinfo=timezone.utc),
                    value=110.0,
                ),
            ],
        )
        assert len(resp.points) == 2
        assert resp.points[1].value == 110.0


class TestMetricSnapshotCreateRequest:
    def test_valid_snapshot_request(self):
        req = MetricSnapshotCreateRequest(
            site_id="550e8400-e29b-41d4-a716-446655440000",
            metric_type="subscriber_count",
            value=150.0,
        )
        assert req.metric_type == "subscriber_count"
        assert req.dimensions is None

    def test_snapshot_with_dimensions(self):
        req = MetricSnapshotCreateRequest(
            site_id="550e8400-e29b-41d4-a716-446655440000",
            metric_type="content_published",
            value=5.0,
            dimensions={"platform": "twitter"},
        )
        assert req.dimensions == {"platform": "twitter"}

    def test_invalid_metric_type(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError, match="Invalid metric_type"):
            MetricSnapshotCreateRequest(
                site_id="550e8400-e29b-41d4-a716-446655440000",
                metric_type="invalid_metric",
                value=1.0,
            )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_analytics/test_analytics_schemas.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.modules.analytics'`

- [ ] **Step 3: Create the schemas**

Create `backend/app/modules/analytics/__init__.py` (empty file).

Create `backend/app/modules/analytics/schemas.py`:

```python
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.metric import METRIC_TYPES


class StatusCount(BaseModel):
    status: str
    count: int


class PlatformCount(BaseModel):
    platform: str
    count: int


class SiteOverviewResponse(BaseModel):
    site_id: str
    total_content: int
    content_by_status: list[StatusCount]
    content_by_platform: list[PlatformCount]
    total_campaigns: int
    total_ads: int
    total_subscribers: int
    active_subscribers: int


class ContentAnalyticsResponse(BaseModel):
    site_id: str
    total: int
    by_status: list[StatusCount]
    by_platform: list[PlatformCount]
    published_count: int
    scheduled_count: int
    draft_count: int


class AdsAnalyticsResponse(BaseModel):
    site_id: str
    total_campaigns: int
    campaigns_by_status: list[StatusCount]
    campaigns_by_platform: list[PlatformCount]
    total_ads: int
    ads_by_status: list[StatusCount]
    total_budget_cents_daily: int


class EmailAnalyticsResponse(BaseModel):
    site_id: str
    total_campaigns: int
    total_sent: int
    total_opened: int
    total_clicked: int
    open_rate: float
    click_rate: float
    total_subscribers: int
    active_subscribers: int


class TimeseriesPoint(BaseModel):
    recorded_at: datetime
    value: float
    dimensions: dict | None = None


class TimeseriesResponse(BaseModel):
    site_id: str
    metric_type: str
    points: list[TimeseriesPoint]


class MetricSnapshotCreateRequest(BaseModel):
    site_id: str
    metric_type: str
    value: float
    dimensions: dict | None = None

    @field_validator("metric_type")
    @classmethod
    def validate_metric_type(cls, v: str) -> str:
        if v not in METRIC_TYPES:
            raise ValueError(
                f"Invalid metric_type '{v}'. Must be one of: {', '.join(METRIC_TYPES)}"
            )
        return v
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_analytics/test_analytics_schemas.py -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/analytics/ backend/tests/test_analytics/test_analytics_schemas.py
git commit -m "feat(analytics): add Pydantic response schemas for analytics endpoints"
```

---

### Task 3: Analytics Service — Site Overview

**Files:**
- Create: `backend/app/services/analytics_service.py`
- Create: `backend/tests/test_analytics/test_analytics_service.py`

- [ ] **Step 1: Write site overview aggregation tests**

Create `backend/tests/test_analytics/test_analytics_service.py`:

```python
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
        # Add content
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

        # Add campaigns and ads
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

        # Add subscribers
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

        # Check by_status contains published=3
        published = next(
            (s for s in overview["content_by_status"] if s["status"] == "published"), None
        )
        assert published is not None
        assert published["count"] == 3

        # Check by_platform contains twitter=2
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
        # Different metric type — should not appear
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_analytics/test_analytics_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.analytics_service'`

- [ ] **Step 3: Implement the analytics service**

Create `backend/app/services/analytics_service.py`:

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.models.ad import AdCampaign, Ad
from app.models.email_campaign import EmailCampaign
from app.models.subscriber import Subscriber
from app.models.metric import MetricSnapshot


class AnalyticsService:
    async def get_site_overview(
        self, db: AsyncSession, site_id: uuid.UUID
    ) -> dict:
        total_content = await self._count(db, Content, Content.site_id == site_id)
        content_by_status = await self._group_count(
            db, Content, Content.status, Content.site_id == site_id
        )
        content_by_platform = await self._group_count(
            db, Content, Content.platform, Content.site_id == site_id
        )
        total_campaigns = await self._count(
            db, AdCampaign, AdCampaign.site_id == site_id
        )
        total_ads = await self._count_ads_for_site(db, site_id)
        total_subscribers = await self._count(
            db, Subscriber, Subscriber.site_id == site_id
        )
        active_subscribers = await self._count(
            db, Subscriber,
            Subscriber.site_id == site_id,
            Subscriber.is_active == True,
        )

        return {
            "total_content": total_content,
            "content_by_status": [
                {"status": s, "count": c} for s, c in content_by_status
            ],
            "content_by_platform": [
                {"platform": p, "count": c} for p, c in content_by_platform
            ],
            "total_campaigns": total_campaigns,
            "total_ads": total_ads,
            "total_subscribers": total_subscribers,
            "active_subscribers": active_subscribers,
        }

    async def get_content_analytics(
        self, db: AsyncSession, site_id: uuid.UUID
    ) -> dict:
        total = await self._count(db, Content, Content.site_id == site_id)
        by_status = await self._group_count(
            db, Content, Content.status, Content.site_id == site_id
        )
        by_platform = await self._group_count(
            db, Content, Content.platform, Content.site_id == site_id
        )

        status_map = {s: c for s, c in by_status}

        return {
            "total": total,
            "by_status": [{"status": s, "count": c} for s, c in by_status],
            "by_platform": [{"platform": p, "count": c} for p, c in by_platform],
            "published_count": status_map.get("published", 0),
            "scheduled_count": status_map.get("scheduled", 0),
            "draft_count": status_map.get("draft", 0),
        }

    async def get_ads_analytics(
        self, db: AsyncSession, site_id: uuid.UUID
    ) -> dict:
        total_campaigns = await self._count(
            db, AdCampaign, AdCampaign.site_id == site_id
        )
        campaigns_by_status = await self._group_count(
            db, AdCampaign, AdCampaign.status, AdCampaign.site_id == site_id
        )
        campaigns_by_platform = await self._group_count(
            db, AdCampaign, AdCampaign.platform, AdCampaign.site_id == site_id
        )
        total_ads = await self._count_ads_for_site(db, site_id)
        ads_by_status = await self._count_ads_by_status_for_site(db, site_id)

        # Sum daily budgets for active campaigns
        budget_result = await db.execute(
            select(func.coalesce(func.sum(AdCampaign.daily_budget_cents), 0))
            .where(AdCampaign.site_id == site_id)
        )
        total_budget = budget_result.scalar()

        return {
            "total_campaigns": total_campaigns,
            "campaigns_by_status": [
                {"status": s, "count": c} for s, c in campaigns_by_status
            ],
            "campaigns_by_platform": [
                {"platform": p, "count": c} for p, c in campaigns_by_platform
            ],
            "total_ads": total_ads,
            "ads_by_status": [{"status": s, "count": c} for s, c in ads_by_status],
            "total_budget_cents_daily": total_budget,
        }

    async def get_email_analytics(
        self, db: AsyncSession, site_id: uuid.UUID
    ) -> dict:
        total_campaigns = await self._count(
            db, EmailCampaign, EmailCampaign.site_id == site_id
        )

        agg_result = await db.execute(
            select(
                func.coalesce(func.sum(EmailCampaign.sent_count), 0),
                func.coalesce(func.sum(EmailCampaign.open_count), 0),
                func.coalesce(func.sum(EmailCampaign.click_count), 0),
            ).where(EmailCampaign.site_id == site_id)
        )
        row = agg_result.one()
        total_sent = row[0]
        total_opened = row[1]
        total_clicked = row[2]

        open_rate = total_opened / total_sent if total_sent > 0 else 0.0
        click_rate = total_clicked / total_sent if total_sent > 0 else 0.0

        total_subscribers = await self._count(
            db, Subscriber, Subscriber.site_id == site_id
        )
        active_subscribers = await self._count(
            db, Subscriber,
            Subscriber.site_id == site_id,
            Subscriber.is_active == True,
        )

        return {
            "total_campaigns": total_campaigns,
            "total_sent": total_sent,
            "total_opened": total_opened,
            "total_clicked": total_clicked,
            "open_rate": open_rate,
            "click_rate": click_rate,
            "total_subscribers": total_subscribers,
            "active_subscribers": active_subscribers,
        }

    async def get_timeseries(
        self,
        db: AsyncSession,
        site_id: uuid.UUID,
        metric_type: str,
        start: datetime,
        end: datetime,
    ) -> list[dict]:
        result = await db.execute(
            select(MetricSnapshot)
            .where(MetricSnapshot.site_id == site_id)
            .where(MetricSnapshot.metric_type == metric_type)
            .where(MetricSnapshot.recorded_at >= start)
            .where(MetricSnapshot.recorded_at <= end)
            .order_by(MetricSnapshot.recorded_at)
        )
        snapshots = result.scalars().all()
        return [
            {
                "recorded_at": s.recorded_at,
                "value": s.value,
                "dimensions": s.dimensions,
            }
            for s in snapshots
        ]

    async def record_snapshot(
        self,
        db: AsyncSession,
        site_id: uuid.UUID,
        metric_type: str,
        value: float,
        dimensions: dict | None = None,
    ) -> MetricSnapshot:
        snapshot = MetricSnapshot(
            site_id=site_id,
            metric_type=metric_type,
            value=value,
            dimensions=dimensions,
            recorded_at=datetime.now(timezone.utc),
        )
        db.add(snapshot)
        await db.commit()
        await db.refresh(snapshot)
        return snapshot

    # ── Private helpers ──────────────────────────────────────────────

    async def _count(self, db: AsyncSession, model, *filters) -> int:
        query = select(func.count()).select_from(model)
        for f in filters:
            query = query.where(f)
        result = await db.execute(query)
        return result.scalar()

    async def _group_count(self, db: AsyncSession, model, group_col, *filters):
        query = select(group_col, func.count()).select_from(model)
        for f in filters:
            query = query.where(f)
        query = query.group_by(group_col)
        result = await db.execute(query)
        return result.all()

    async def _count_ads_for_site(self, db: AsyncSession, site_id: uuid.UUID) -> int:
        result = await db.execute(
            select(func.count())
            .select_from(Ad)
            .join(AdCampaign, Ad.campaign_id == AdCampaign.id)
            .where(AdCampaign.site_id == site_id)
        )
        return result.scalar()

    async def _count_ads_by_status_for_site(self, db: AsyncSession, site_id: uuid.UUID):
        result = await db.execute(
            select(Ad.status, func.count())
            .join(AdCampaign, Ad.campaign_id == AdCampaign.id)
            .where(AdCampaign.site_id == site_id)
            .group_by(Ad.status)
        )
        return result.all()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_analytics/test_analytics_service.py -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/analytics_service.py backend/tests/test_analytics/test_analytics_service.py
git commit -m "feat(analytics): add analytics service with aggregation queries"
```

---

### Task 4: Analytics Router

**Files:**
- Create: `backend/app/modules/analytics/router.py`
- Create: `backend/tests/test_analytics/test_analytics_router.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write router tests**

Create `backend/tests/test_analytics/test_analytics_router.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail (if router import is tested) or pass (service-only)**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_analytics/test_analytics_router.py -v`

- [ ] **Step 3: Implement the analytics router**

Create `backend/app/modules/analytics/router.py`:

```python
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.site import Site
from app.modules.auth.dependencies import get_current_user
from app.modules.analytics.schemas import (
    SiteOverviewResponse,
    ContentAnalyticsResponse,
    AdsAnalyticsResponse,
    EmailAnalyticsResponse,
    TimeseriesResponse,
    TimeseriesPoint,
    MetricSnapshotCreateRequest,
    StatusCount,
    PlatformCount,
)
from app.services.analytics_service import AnalyticsService
from sqlalchemy import select

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

_service = AnalyticsService()


async def _verify_site(db: AsyncSession, site_id: str) -> None:
    result = await db.execute(
        select(Site).where(Site.id == uuid.UUID(site_id))
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Site not found")


@router.get("/overview", response_model=SiteOverviewResponse)
async def get_overview(
    site_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await _verify_site(db, site_id)
    data = await _service.get_site_overview(db, uuid.UUID(site_id))
    return SiteOverviewResponse(
        site_id=site_id,
        total_content=data["total_content"],
        content_by_status=[StatusCount(**s) for s in data["content_by_status"]],
        content_by_platform=[PlatformCount(**p) for p in data["content_by_platform"]],
        total_campaigns=data["total_campaigns"],
        total_ads=data["total_ads"],
        total_subscribers=data["total_subscribers"],
        active_subscribers=data["active_subscribers"],
    )


@router.get("/content", response_model=ContentAnalyticsResponse)
async def get_content_analytics(
    site_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await _verify_site(db, site_id)
    data = await _service.get_content_analytics(db, uuid.UUID(site_id))
    return ContentAnalyticsResponse(
        site_id=site_id,
        total=data["total"],
        by_status=[StatusCount(**s) for s in data["by_status"]],
        by_platform=[PlatformCount(**p) for p in data["by_platform"]],
        published_count=data["published_count"],
        scheduled_count=data["scheduled_count"],
        draft_count=data["draft_count"],
    )


@router.get("/ads", response_model=AdsAnalyticsResponse)
async def get_ads_analytics(
    site_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await _verify_site(db, site_id)
    data = await _service.get_ads_analytics(db, uuid.UUID(site_id))
    return AdsAnalyticsResponse(
        site_id=site_id,
        total_campaigns=data["total_campaigns"],
        campaigns_by_status=[StatusCount(**s) for s in data["campaigns_by_status"]],
        campaigns_by_platform=[PlatformCount(**p) for p in data["campaigns_by_platform"]],
        total_ads=data["total_ads"],
        ads_by_status=[StatusCount(**s) for s in data["ads_by_status"]],
        total_budget_cents_daily=data["total_budget_cents_daily"],
    )


@router.get("/email", response_model=EmailAnalyticsResponse)
async def get_email_analytics(
    site_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await _verify_site(db, site_id)
    data = await _service.get_email_analytics(db, uuid.UUID(site_id))
    return EmailAnalyticsResponse(
        site_id=site_id,
        total_campaigns=data["total_campaigns"],
        total_sent=data["total_sent"],
        total_opened=data["total_opened"],
        total_clicked=data["total_clicked"],
        open_rate=data["open_rate"],
        click_rate=data["click_rate"],
        total_subscribers=data["total_subscribers"],
        active_subscribers=data["active_subscribers"],
    )


@router.get("/timeseries", response_model=TimeseriesResponse)
async def get_timeseries(
    site_id: str = Query(...),
    metric_type: str = Query(...),
    start: datetime = Query(...),
    end: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await _verify_site(db, site_id)
    points = await _service.get_timeseries(
        db, uuid.UUID(site_id), metric_type, start, end
    )
    return TimeseriesResponse(
        site_id=site_id,
        metric_type=metric_type,
        points=[TimeseriesPoint(**p) for p in points],
    )


@router.post("/snapshot", status_code=status.HTTP_201_CREATED)
async def record_snapshot(
    request: MetricSnapshotCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await _verify_site(db, request.site_id)
    snapshot = await _service.record_snapshot(
        db,
        site_id=uuid.UUID(request.site_id),
        metric_type=request.metric_type,
        value=request.value,
        dimensions=request.dimensions,
    )
    return {"id": str(snapshot.id), "recorded_at": snapshot.recorded_at.isoformat()}
```

- [ ] **Step 4: Register the analytics router in main.py**

Current `backend/app/main.py` has auth, content, and ads routers. Add after the ads router:

```python
    from app.modules.analytics.router import router as analytics_router
    app.include_router(analytics_router)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_analytics/test_analytics_router.py -v`
Expected: All 7 tests PASS

- [ ] **Step 6: Run full test suite for regression**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest -v`
Expected: All existing + new tests PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/modules/analytics/router.py backend/app/main.py backend/tests/test_analytics/test_analytics_router.py
git commit -m "feat(analytics): add analytics router with overview, content, ads, email, timeseries endpoints"
```

---

### Task 5: Full Integration Verification

**Files:** None new — verification only.

- [ ] **Step 1: Run the full test suite**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest -v --tb=short`
Expected: All tests PASS

- [ ] **Step 2: Verify app loads with analytics routes**

Run: `cd /home/arun/market/amplifi/backend && python -c "from app.main import app; print('Routes:', [r.path for r in app.routes if 'analytics' in r.path])"`
Expected: Output includes `/api/analytics/overview`, `/api/analytics/content`, `/api/analytics/ads`, `/api/analytics/email`, `/api/analytics/timeseries`, `/api/analytics/snapshot`

- [ ] **Step 3: Commit any remaining changes**

```bash
git status
# If clean, no action needed
```
