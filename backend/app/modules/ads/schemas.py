from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.ad import AD_PLATFORMS, CAMPAIGN_STATUSES, CAMPAIGN_OBJECTIVES, AD_STATUSES


class CampaignCreateRequest(BaseModel):
    site_id: str
    name: str
    platform: str
    objective: str
    daily_budget_cents: int = Field(gt=0)
    status: str = "draft"
    targeting: dict | None = None
    meta_data: dict | None = None

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        if v not in AD_PLATFORMS:
            raise ValueError(
                f"Invalid platform '{v}'. Must be one of: {', '.join(AD_PLATFORMS)}"
            )
        return v

    @field_validator("objective")
    @classmethod
    def validate_objective(cls, v: str) -> str:
        if v not in CAMPAIGN_OBJECTIVES:
            raise ValueError(
                f"Invalid objective '{v}'. Must be one of: {', '.join(CAMPAIGN_OBJECTIVES)}"
            )
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in CAMPAIGN_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(CAMPAIGN_STATUSES)}"
            )
        return v


class CampaignUpdateRequest(BaseModel):
    name: str | None = None
    platform: str | None = None
    objective: str | None = None
    daily_budget_cents: int | None = Field(None, gt=0)
    status: str | None = None
    targeting: dict | None = None
    meta_data: dict | None = None

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str | None) -> str | None:
        if v is not None and v not in AD_PLATFORMS:
            raise ValueError(
                f"Invalid platform '{v}'. Must be one of: {', '.join(AD_PLATFORMS)}"
            )
        return v

    @field_validator("objective")
    @classmethod
    def validate_objective(cls, v: str | None) -> str | None:
        if v is not None and v not in CAMPAIGN_OBJECTIVES:
            raise ValueError(
                f"Invalid objective '{v}'. Must be one of: {', '.join(CAMPAIGN_OBJECTIVES)}"
            )
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in CAMPAIGN_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(CAMPAIGN_STATUSES)}"
            )
        return v


class CampaignResponse(BaseModel):
    id: str
    site_id: str
    user_id: str
    name: str
    platform: str
    objective: str
    daily_budget_cents: int
    status: str
    targeting: dict | None = None
    meta_data: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CampaignListResponse(BaseModel):
    items: list[CampaignResponse]
    total: int


class AdCreateRequest(BaseModel):
    campaign_id: str
    headline: str = Field(max_length=150)
    headline_2: str | None = Field(None, max_length=150)
    headline_3: str | None = Field(None, max_length=150)
    description: str
    description_2: str | None = None
    display_url: str | None = None
    final_url: str
    image_url: str | None = None
    status: str = "draft"
    meta_data: dict | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in AD_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(AD_STATUSES)}"
            )
        return v


class AdUpdateRequest(BaseModel):
    headline: str | None = Field(None, max_length=150)
    headline_2: str | None = Field(None, max_length=150)
    headline_3: str | None = Field(None, max_length=150)
    description: str | None = None
    description_2: str | None = None
    display_url: str | None = None
    final_url: str | None = None
    image_url: str | None = None
    status: str | None = None
    meta_data: dict | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in AD_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(AD_STATUSES)}"
            )
        return v


class AdResponse(BaseModel):
    id: str
    campaign_id: str
    headline: str
    headline_2: str | None = None
    headline_3: str | None = None
    description: str
    description_2: str | None = None
    display_url: str | None = None
    final_url: str
    image_url: str | None = None
    status: str
    platform_ad_id: str | None = None
    meta_data: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdListResponse(BaseModel):
    items: list[AdResponse]
    total: int


class AdGenerateRequest(BaseModel):
    campaign_id: str
    site_id: str
    platform: str
    topic: str
    tone: str = "professional"
    keywords: list[str] = []
    num_variants: int = Field(3, ge=1, le=10)

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        if v not in AD_PLATFORMS:
            raise ValueError(
                f"Invalid platform '{v}'. Must be one of: {', '.join(AD_PLATFORMS)}"
            )
        return v


class AdGenerateResponse(BaseModel):
    ads: list[AdResponse]
