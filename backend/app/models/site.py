import uuid

from sqlalchemy import ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Site(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sites"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    niche: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scraped_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    target_geographies: Mapped[list | None] = mapped_column(JSON, nullable=True)
    target_timezones: Mapped[list | None] = mapped_column(JSON, nullable=True)
