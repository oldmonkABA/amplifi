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
