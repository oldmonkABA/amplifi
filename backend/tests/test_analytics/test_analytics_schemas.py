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
