import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


AD_PLATFORMS = ["google_ads", "facebook_ads"]

CAMPAIGN_STATUSES = ["draft", "active", "paused", "completed"]

CAMPAIGN_OBJECTIVES = ["traffic", "conversions", "awareness", "leads"]

AD_STATUSES = ["draft", "active", "paused", "rejected"]


class AdCampaign(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ad_campaigns"

    site_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sites.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    objective: Mapped[str] = mapped_column(String(50), nullable=False)
    daily_budget_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    targeting: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Ad(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ads"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ad_campaigns.id"), nullable=False, index=True
    )
    headline: Mapped[str] = mapped_column(String(150), nullable=False)
    headline_2: Mapped[str | None] = mapped_column(String(150), nullable=True)
    headline_3: Mapped[str | None] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    final_url: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    platform_ad_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
