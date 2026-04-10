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
