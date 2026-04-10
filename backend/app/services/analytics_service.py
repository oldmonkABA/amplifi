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
