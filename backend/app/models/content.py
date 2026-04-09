import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


PLATFORMS = [
    "twitter", "linkedin", "reddit", "blog", "medium",
    "quora", "telegram", "youtube", "hackernews", "producthunt", "email",
]

CONTENT_STATUSES = ["draft", "approved", "scheduled", "published", "rejected"]


class ContentGroup(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "content_groups"

    site_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sites.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class Content(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contents"

    site_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sites.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    group_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("content_groups.id"), nullable=True, index=True
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    target_timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    platform_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
