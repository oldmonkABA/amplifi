from datetime import datetime

from pydantic import BaseModel, field_validator


VALID_PLATFORMS = [
    "twitter", "linkedin", "reddit", "blog", "medium",
    "quora", "telegram", "youtube", "hackernews", "producthunt", "email",
]

VALID_STATUSES = ["draft", "approved", "scheduled", "published", "rejected"]


class ContentCreateRequest(BaseModel):
    site_id: str
    platform: str
    content_type: str
    title: str
    body: str
    status: str = "draft"
    group_id: str | None = None
    scheduled_at: datetime | None = None
    target_timezone: str | None = None
    meta_data: dict | None = None

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        if v not in VALID_PLATFORMS:
            raise ValueError(
                f"Invalid platform '{v}'. Must be one of: {', '.join(VALID_PLATFORMS)}"
            )
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        return v


class ContentUpdateRequest(BaseModel):
    title: str | None = None
    body: str | None = None
    status: str | None = None
    scheduled_at: datetime | None = None
    target_timezone: str | None = None
    meta_data: dict | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        return v


class ContentResponse(BaseModel):
    id: str
    site_id: str
    user_id: str
    platform: str
    content_type: str
    title: str
    body: str
    status: str
    group_id: str | None = None
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    target_timezone: str | None = None
    platform_post_id: str | None = None
    meta_data: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContentListResponse(BaseModel):
    items: list[ContentResponse]
    total: int


class ContentGroupCreateRequest(BaseModel):
    site_id: str
    name: str
    description: str | None = None


class ContentGroupResponse(BaseModel):
    id: str
    site_id: str
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContentGenerateRequest(BaseModel):
    site_id: str
    platform: str
    content_type: str
    topic: str
    tone: str = "professional"
    keywords: list[str] = []
    additional_context: str | None = None

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        if v not in VALID_PLATFORMS:
            raise ValueError(
                f"Invalid platform '{v}'. Must be one of: {', '.join(VALID_PLATFORMS)}"
            )
        return v


class ContentScheduleRequest(BaseModel):
    scheduled_at: datetime
    target_timezone: str | None = None


class ContentCalendarResponse(BaseModel):
    items: list[ContentResponse]
