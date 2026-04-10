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
