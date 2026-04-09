import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Subscriber(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subscribers"

    site_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sites.id"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    drip_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="not_started"
    )
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    unsubscribe_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
