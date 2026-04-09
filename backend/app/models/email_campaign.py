import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


CAMPAIGN_TYPES = ["drip", "digest", "one_off"]
CAMPAIGN_STATUSES = ["draft", "scheduled", "sending", "sent", "failed"]


class EmailCampaign(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "email_campaigns"

    site_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sites.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    campaign_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", index=True
    )
    audience_segment: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sent_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    open_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    click_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
