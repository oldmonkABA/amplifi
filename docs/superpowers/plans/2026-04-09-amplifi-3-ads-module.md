# Ads Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an Ads module that lets users create ad campaigns, generate AI-powered ad copy for Google Ads and Facebook Ads, and manage ads through a full CRUD API — following the same patterns as the existing Content module.

**Architecture:** Two new models (AdCampaign, Ad) with a module at `app/modules/ads/` containing router + schemas. An `AdCopyGenerator` service uses the existing LLM factory to produce platform-specific ad copy (headlines, descriptions). An `AdPlatformManager` abstraction (factory + registry pattern, matching `publishing/`) provides a future integration point for live platform APIs while shipping with a mock implementation for now.

**Tech Stack:** FastAPI, SQLAlchemy async, Pydantic v2, pytest + pytest-asyncio, existing LLM factory

---

## File Structure

### New Files

| File | Responsibility |
|------|---------------|
| `backend/app/models/ad.py` | AdCampaign and Ad SQLAlchemy models |
| `backend/app/modules/ads/__init__.py` | Package init |
| `backend/app/modules/ads/router.py` | All ads API endpoints |
| `backend/app/modules/ads/schemas.py` | Pydantic request/response schemas |
| `backend/app/services/ad_copy_generator.py` | LLM-powered ad copy generation |
| `backend/app/services/ad_platforms/__init__.py` | Package init |
| `backend/app/services/ad_platforms/base.py` | Abstract base + result dataclass |
| `backend/app/services/ad_platforms/factory.py` | Registry factory for ad platforms |
| `backend/app/services/ad_platforms/google_ads.py` | Google Ads manager (mock) |
| `backend/app/services/ad_platforms/facebook_ads.py` | Facebook Ads manager (mock) |
| `backend/tests/test_ads/__init__.py` | Test package init |
| `backend/tests/test_ads/test_ad_models.py` | Model tests |
| `backend/tests/test_ads/test_ad_schemas.py` | Schema validation tests |
| `backend/tests/test_ads/test_ad_router.py` | Router/endpoint tests |
| `backend/tests/test_ads/test_ad_copy_generator.py` | Ad copy generator tests |
| `backend/tests/test_ads/test_ad_platforms.py` | Ad platform abstraction tests |

### Modified Files

| File | Change |
|------|--------|
| `backend/app/models/__init__.py` | Add AdCampaign, Ad imports |
| `backend/app/main.py` | Include ads router |

---

### Task 1: Ad Models

**Files:**
- Create: `backend/app/models/ad.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_ads/test_ad_models.py`

- [ ] **Step 1: Create test package and write model tests**

Create `backend/tests/test_ads/__init__.py` (empty file).

Create `backend/tests/test_ads/test_ad_models.py`:

```python
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.site import Site
from app.models.ad import AdCampaign, Ad, AD_PLATFORMS, CAMPAIGN_STATUSES, AD_STATUSES


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    user = User(
        email="ads@test.com",
        name="Ads Tester",
        google_id="google_ads_123",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def site(db_session: AsyncSession, user: User) -> Site:
    site = Site(
        user_id=user.id,
        url="https://example.com",
        name="Test Site",
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site


@pytest.fixture
async def campaign(db_session: AsyncSession, user: User, site: Site) -> AdCampaign:
    campaign = AdCampaign(
        site_id=site.id,
        user_id=user.id,
        name="Test Campaign",
        platform="google_ads",
        objective="traffic",
        daily_budget_cents=5000,
        status="draft",
    )
    db_session.add(campaign)
    await db_session.commit()
    await db_session.refresh(campaign)
    return campaign


class TestAdCampaignModel:
    @pytest.mark.asyncio
    async def test_create_campaign(self, db_session: AsyncSession, user: User, site: Site):
        campaign = AdCampaign(
            site_id=site.id,
            user_id=user.id,
            name="My Campaign",
            platform="google_ads",
            objective="conversions",
            daily_budget_cents=10000,
            status="draft",
        )
        db_session.add(campaign)
        await db_session.commit()
        await db_session.refresh(campaign)

        assert campaign.id is not None
        assert campaign.name == "My Campaign"
        assert campaign.platform == "google_ads"
        assert campaign.objective == "conversions"
        assert campaign.daily_budget_cents == 10000
        assert campaign.status == "draft"
        assert campaign.created_at is not None
        assert campaign.updated_at is not None

    @pytest.mark.asyncio
    async def test_campaign_optional_fields(self, db_session: AsyncSession, user: User, site: Site):
        campaign = AdCampaign(
            site_id=site.id,
            user_id=user.id,
            name="Minimal Campaign",
            platform="facebook_ads",
            objective="awareness",
            daily_budget_cents=2000,
            status="draft",
            targeting={"age_min": 25, "age_max": 55, "interests": ["finance"]},
            meta_data={"notes": "test"},
        )
        db_session.add(campaign)
        await db_session.commit()
        await db_session.refresh(campaign)

        assert campaign.targeting == {"age_min": 25, "age_max": 55, "interests": ["finance"]}
        assert campaign.meta_data == {"notes": "test"}

    @pytest.mark.asyncio
    async def test_query_campaigns_by_site(self, db_session: AsyncSession, user: User, site: Site):
        for i in range(3):
            db_session.add(AdCampaign(
                site_id=site.id,
                user_id=user.id,
                name=f"Campaign {i}",
                platform="google_ads",
                objective="traffic",
                daily_budget_cents=1000,
                status="draft",
            ))
        await db_session.commit()

        result = await db_session.execute(
            select(AdCampaign).where(AdCampaign.site_id == site.id)
        )
        campaigns = result.scalars().all()
        assert len(campaigns) == 3

    @pytest.mark.asyncio
    async def test_campaign_constants(self):
        assert "google_ads" in AD_PLATFORMS
        assert "facebook_ads" in AD_PLATFORMS
        assert "draft" in CAMPAIGN_STATUSES
        assert "active" in CAMPAIGN_STATUSES
        assert "paused" in CAMPAIGN_STATUSES
        assert "completed" in CAMPAIGN_STATUSES


class TestAdModel:
    @pytest.mark.asyncio
    async def test_create_ad(self, db_session: AsyncSession, campaign: AdCampaign):
        ad = Ad(
            campaign_id=campaign.id,
            headline="Best Finance App",
            description="Track your portfolio with AI-powered insights.",
            display_url="example.com",
            final_url="https://example.com/signup",
            status="draft",
        )
        db_session.add(ad)
        await db_session.commit()
        await db_session.refresh(ad)

        assert ad.id is not None
        assert ad.campaign_id == campaign.id
        assert ad.headline == "Best Finance App"
        assert ad.description == "Track your portfolio with AI-powered insights."
        assert ad.display_url == "example.com"
        assert ad.final_url == "https://example.com/signup"
        assert ad.status == "draft"

    @pytest.mark.asyncio
    async def test_ad_optional_fields(self, db_session: AsyncSession, campaign: AdCampaign):
        ad = Ad(
            campaign_id=campaign.id,
            headline="Finance Tracker",
            description="AI insights for your money.",
            final_url="https://example.com",
            status="draft",
            headline_2="Smart Portfolio",
            headline_3="Free Trial",
            description_2="Join 10k users.",
            image_url="https://cdn.example.com/ad.png",
            meta_data={"variant": "A"},
        )
        db_session.add(ad)
        await db_session.commit()
        await db_session.refresh(ad)

        assert ad.headline_2 == "Smart Portfolio"
        assert ad.headline_3 == "Free Trial"
        assert ad.description_2 == "Join 10k users."
        assert ad.image_url == "https://cdn.example.com/ad.png"
        assert ad.meta_data == {"variant": "A"}

    @pytest.mark.asyncio
    async def test_query_ads_by_campaign(self, db_session: AsyncSession, campaign: AdCampaign):
        for i in range(3):
            db_session.add(Ad(
                campaign_id=campaign.id,
                headline=f"Headline {i}",
                description=f"Description {i}",
                final_url="https://example.com",
                status="draft",
            ))
        await db_session.commit()

        result = await db_session.execute(
            select(Ad).where(Ad.campaign_id == campaign.id)
        )
        ads = result.scalars().all()
        assert len(ads) == 3

    @pytest.mark.asyncio
    async def test_ad_constants(self):
        assert "draft" in AD_STATUSES
        assert "active" in AD_STATUSES
        assert "paused" in AD_STATUSES
        assert "rejected" in AD_STATUSES
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_ads/test_ad_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.models.ad'`

- [ ] **Step 3: Create the Ad models**

Create `backend/app/models/ad.py`:

```python
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
```

- [ ] **Step 4: Register models in `__init__.py`**

Add to `backend/app/models/__init__.py`:

```python
from app.models.ad import AdCampaign, Ad
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_ads/test_ad_models.py -v`
Expected: All 8 tests PASS

- [ ] **Step 6: Run full test suite for regression**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest -v`
Expected: All 116 existing tests + 8 new tests PASS (124 total)

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/ad.py backend/app/models/__init__.py backend/tests/test_ads/
git commit -m "feat(ads): add AdCampaign and Ad models"
```

---

### Task 2: Ads Schemas

**Files:**
- Create: `backend/app/modules/ads/__init__.py`
- Create: `backend/app/modules/ads/schemas.py`
- Test: `backend/tests/test_ads/test_ad_schemas.py`

- [ ] **Step 1: Write schema validation tests**

Create `backend/tests/test_ads/test_ad_schemas.py`:

```python
import pytest
from pydantic import ValidationError

from app.modules.ads.schemas import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
    AdCreateRequest,
    AdUpdateRequest,
    AdGenerateRequest,
    CampaignResponse,
    AdResponse,
)


class TestCampaignCreateRequest:
    def test_valid_campaign(self):
        req = CampaignCreateRequest(
            site_id="550e8400-e29b-41d4-a716-446655440000",
            name="Test Campaign",
            platform="google_ads",
            objective="traffic",
            daily_budget_cents=5000,
        )
        assert req.platform == "google_ads"
        assert req.status == "draft"

    def test_invalid_platform(self):
        with pytest.raises(ValidationError, match="Invalid platform"):
            CampaignCreateRequest(
                site_id="550e8400-e29b-41d4-a716-446655440000",
                name="Test",
                platform="tiktok_ads",
                objective="traffic",
                daily_budget_cents=5000,
            )

    def test_invalid_objective(self):
        with pytest.raises(ValidationError, match="Invalid objective"):
            CampaignCreateRequest(
                site_id="550e8400-e29b-41d4-a716-446655440000",
                name="Test",
                platform="google_ads",
                objective="viral",
                daily_budget_cents=5000,
            )

    def test_invalid_status(self):
        with pytest.raises(ValidationError, match="Invalid status"):
            CampaignCreateRequest(
                site_id="550e8400-e29b-41d4-a716-446655440000",
                name="Test",
                platform="google_ads",
                objective="traffic",
                daily_budget_cents=5000,
                status="deleted",
            )

    def test_budget_must_be_positive(self):
        with pytest.raises(ValidationError):
            CampaignCreateRequest(
                site_id="550e8400-e29b-41d4-a716-446655440000",
                name="Test",
                platform="google_ads",
                objective="traffic",
                daily_budget_cents=-100,
            )


class TestCampaignUpdateRequest:
    def test_partial_update(self):
        req = CampaignUpdateRequest(name="Updated Name")
        assert req.name == "Updated Name"
        assert req.platform is None

    def test_invalid_status_on_update(self):
        with pytest.raises(ValidationError, match="Invalid status"):
            CampaignUpdateRequest(status="deleted")


class TestAdCreateRequest:
    def test_valid_ad(self):
        req = AdCreateRequest(
            campaign_id="550e8400-e29b-41d4-a716-446655440000",
            headline="Best Product",
            description="Buy now.",
            final_url="https://example.com",
        )
        assert req.headline == "Best Product"
        assert req.status == "draft"

    def test_headline_too_long(self):
        with pytest.raises(ValidationError):
            AdCreateRequest(
                campaign_id="550e8400-e29b-41d4-a716-446655440000",
                headline="A" * 151,
                description="Buy now.",
                final_url="https://example.com",
            )


class TestAdUpdateRequest:
    def test_partial_update(self):
        req = AdUpdateRequest(headline="New Headline")
        assert req.headline == "New Headline"
        assert req.description is None


class TestAdGenerateRequest:
    def test_valid_generate_request(self):
        req = AdGenerateRequest(
            campaign_id="550e8400-e29b-41d4-a716-446655440000",
            site_id="550e8400-e29b-41d4-a716-446655440001",
            platform="google_ads",
            topic="AI portfolio tracker",
            num_variants=3,
        )
        assert req.num_variants == 3
        assert req.tone == "professional"

    def test_invalid_platform(self):
        with pytest.raises(ValidationError, match="Invalid platform"):
            AdGenerateRequest(
                campaign_id="550e8400-e29b-41d4-a716-446655440000",
                site_id="550e8400-e29b-41d4-a716-446655440001",
                platform="snapchat_ads",
                topic="test",
            )

    def test_num_variants_bounds(self):
        with pytest.raises(ValidationError):
            AdGenerateRequest(
                campaign_id="550e8400-e29b-41d4-a716-446655440000",
                site_id="550e8400-e29b-41d4-a716-446655440001",
                platform="google_ads",
                topic="test",
                num_variants=0,
            )
        with pytest.raises(ValidationError):
            AdGenerateRequest(
                campaign_id="550e8400-e29b-41d4-a716-446655440000",
                site_id="550e8400-e29b-41d4-a716-446655440001",
                platform="google_ads",
                topic="test",
                num_variants=11,
            )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_ads/test_ad_schemas.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.modules.ads'`

- [ ] **Step 3: Create the schemas**

Create `backend/app/modules/ads/__init__.py` (empty file).

Create `backend/app/modules/ads/schemas.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_ads/test_ad_schemas.py -v`
Expected: All 11 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/ads/ backend/tests/test_ads/test_ad_schemas.py
git commit -m "feat(ads): add Pydantic schemas for campaigns and ads"
```

---

### Task 3: Ad Copy Generator Service

**Files:**
- Create: `backend/app/services/ad_copy_generator.py`
- Test: `backend/tests/test_ads/test_ad_copy_generator.py`

- [ ] **Step 1: Write ad copy generator tests**

Create `backend/tests/test_ads/test_ad_copy_generator.py`:

```python
import json
from unittest.mock import AsyncMock

import pytest

from app.services.ad_copy_generator import AdCopyGenerator, AD_PLATFORM_CONFIGS


class TestAdCopyGeneratorConfigs:
    def test_google_ads_config_exists(self):
        assert "google_ads" in AD_PLATFORM_CONFIGS
        config = AD_PLATFORM_CONFIGS["google_ads"]
        assert "headline_max" in config
        assert "description_max" in config
        assert "system_prompt" in config
        assert config["headline_max"] == 30
        assert config["description_max"] == 90

    def test_facebook_ads_config_exists(self):
        assert "facebook_ads" in AD_PLATFORM_CONFIGS
        config = AD_PLATFORM_CONFIGS["facebook_ads"]
        assert config["headline_max"] == 40
        assert config["description_max"] == 125


class TestAdCopyGenerator:
    @pytest.fixture
    def mock_llm(self):
        return AsyncMock()

    @pytest.fixture
    def generator(self, mock_llm):
        return AdCopyGenerator(llm=mock_llm)

    @pytest.mark.asyncio
    async def test_generate_returns_variants(self, generator, mock_llm):
        mock_llm.generate.return_value = json.dumps([
            {
                "headline": "Track Investments",
                "headline_2": "AI-Powered",
                "headline_3": "Free Trial",
                "description": "Smart portfolio tracking with AI insights.",
                "description_2": "Join 10k users managing their wealth.",
            },
            {
                "headline": "Smart Finance",
                "headline_2": "Real-Time Data",
                "headline_3": "Start Free",
                "description": "AI-powered investment tracking made simple.",
                "description_2": "Get started in under 2 minutes.",
            },
        ])

        variants = await generator.generate(
            platform="google_ads",
            topic="AI portfolio tracker",
            num_variants=2,
        )

        assert len(variants) == 2
        assert variants[0]["headline"] == "Track Investments"
        assert variants[0]["description"] == "Smart portfolio tracking with AI insights."
        assert variants[1]["headline"] == "Smart Finance"
        mock_llm.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_site_context(self, generator, mock_llm):
        mock_llm.generate.return_value = json.dumps([
            {
                "headline": "CautilyaCapital",
                "description": "Expert finance insights.",
            },
        ])

        variants = await generator.generate(
            platform="facebook_ads",
            topic="finance blog",
            num_variants=1,
            site_context={"product_name": "CautilyaCapital", "niche": "finance"},
        )

        assert len(variants) == 1
        # Verify site context was included in the prompt
        call_args = mock_llm.generate.call_args
        assert "CautilyaCapital" in call_args.kwargs.get("prompt", call_args[0][0] if call_args[0] else "")

    @pytest.mark.asyncio
    async def test_generate_with_keywords(self, generator, mock_llm):
        mock_llm.generate.return_value = json.dumps([
            {"headline": "Test", "description": "Test desc."},
        ])

        await generator.generate(
            platform="google_ads",
            topic="investments",
            num_variants=1,
            keywords=["portfolio", "AI"],
        )

        call_args = mock_llm.generate.call_args
        prompt = call_args.kwargs.get("prompt", call_args[0][0] if call_args[0] else "")
        assert "portfolio" in prompt
        assert "AI" in prompt

    @pytest.mark.asyncio
    async def test_generate_unsupported_platform(self, generator):
        with pytest.raises(ValueError, match="Unsupported ad platform"):
            await generator.generate(
                platform="tiktok_ads",
                topic="test",
                num_variants=1,
            )

    @pytest.mark.asyncio
    async def test_generate_handles_json_with_markdown_fences(self, generator, mock_llm):
        mock_llm.generate.return_value = '```json\n[{"headline": "Test", "description": "Desc."}]\n```'

        variants = await generator.generate(
            platform="google_ads",
            topic="test",
            num_variants=1,
        )

        assert len(variants) == 1
        assert variants[0]["headline"] == "Test"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_ads/test_ad_copy_generator.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.ad_copy_generator'`

- [ ] **Step 3: Implement the ad copy generator**

Create `backend/app/services/ad_copy_generator.py`:

```python
import json
import re


AD_PLATFORM_CONFIGS = {
    "google_ads": {
        "headline_max": 30,
        "description_max": 90,
        "num_headlines": 3,
        "num_descriptions": 2,
        "system_prompt": (
            "You are a Google Ads copywriter. Write compelling search ad copy. "
            "Headlines must be under 30 characters each. Descriptions under 90 characters. "
            "Focus on strong CTAs, unique value propositions, and keyword relevance. "
            "Return ONLY a JSON array — no markdown fences, no commentary."
        ),
    },
    "facebook_ads": {
        "headline_max": 40,
        "description_max": 125,
        "num_headlines": 1,
        "num_descriptions": 1,
        "system_prompt": (
            "You are a Facebook Ads copywriter. Write scroll-stopping ad copy. "
            "Headlines must be under 40 characters. Descriptions under 125 characters. "
            "Focus on emotional hooks, social proof, and clear CTAs. "
            "Return ONLY a JSON array — no markdown fences, no commentary."
        ),
    },
}


class AdCopyGenerator:
    """Generates platform-specific ad copy using LLM."""

    def __init__(self, llm):
        self.llm = llm

    async def generate(
        self,
        platform: str,
        topic: str,
        num_variants: int = 3,
        site_context: dict | None = None,
        tone: str = "professional",
        keywords: list[str] | None = None,
    ) -> list[dict]:
        config = AD_PLATFORM_CONFIGS.get(platform)
        if not config:
            raise ValueError(f"Unsupported ad platform: {platform}")

        prompt = self._build_prompt(
            platform=platform,
            topic=topic,
            num_variants=num_variants,
            site_context=site_context or {},
            tone=tone,
            keywords=keywords or [],
            config=config,
        )

        response = await self.llm.generate(prompt=prompt)
        return self._parse_response(response)

    def _build_prompt(
        self,
        platform: str,
        topic: str,
        num_variants: int,
        site_context: dict,
        tone: str,
        keywords: list[str],
        config: dict,
    ) -> str:
        parts = [config["system_prompt"], ""]

        if site_context:
            context_str = ", ".join(f"{k}: {v}" for k, v in site_context.items())
            parts.append(f"Product context: {context_str}")

        parts.append(f"Platform: {platform}")
        parts.append(f"Topic: {topic}")
        parts.append(f"Tone: {tone}")
        parts.append(f"Headline max length: {config['headline_max']} characters")
        parts.append(f"Description max length: {config['description_max']} characters")

        if keywords:
            parts.append(f"Target keywords: {', '.join(keywords)}")

        fields = ["headline", "description"]
        if config["num_headlines"] > 1:
            fields.extend(f"headline_{i}" for i in range(2, config["num_headlines"] + 1))
        if config["num_descriptions"] > 1:
            fields.extend(f"description_{i}" for i in range(2, config["num_descriptions"] + 1))

        parts.append("")
        parts.append(
            f"Generate exactly {num_variants} ad variant(s) as a JSON array. "
            f"Each object must have these keys: {', '.join(fields)}. "
            f"Return ONLY the JSON array, no other text."
        )

        return "\n".join(parts)

    def _parse_response(self, response: str) -> list[dict]:
        text = response.strip()
        # Strip markdown fences if present
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()
        return json.loads(text)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_ads/test_ad_copy_generator.py -v`
Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/ad_copy_generator.py backend/tests/test_ads/test_ad_copy_generator.py
git commit -m "feat(ads): add LLM-powered ad copy generator service"
```

---

### Task 4: Ad Platform Abstraction

**Files:**
- Create: `backend/app/services/ad_platforms/__init__.py`
- Create: `backend/app/services/ad_platforms/base.py`
- Create: `backend/app/services/ad_platforms/factory.py`
- Create: `backend/app/services/ad_platforms/google_ads.py`
- Create: `backend/app/services/ad_platforms/facebook_ads.py`
- Test: `backend/tests/test_ads/test_ad_platforms.py`

- [ ] **Step 1: Write platform abstraction tests**

Create `backend/tests/test_ads/test_ad_platforms.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch

from app.services.ad_platforms.base import AdPlatformManager, AdPlatformResult
from app.services.ad_platforms.factory import AdPlatformFactory
from app.services.ad_platforms.google_ads import GoogleAdsManager
from app.services.ad_platforms.facebook_ads import FacebookAdsManager


class TestAdPlatformResult:
    def test_success_result(self):
        result = AdPlatformResult(
            success=True,
            platform="google_ads",
            ad_id="ad_123",
        )
        assert result.success is True
        assert result.platform == "google_ads"
        assert result.ad_id == "ad_123"
        assert result.error is None

    def test_failure_result(self):
        result = AdPlatformResult(
            success=False,
            platform="facebook_ads",
            error="Authentication failed",
        )
        assert result.success is False
        assert result.ad_id is None
        assert result.error == "Authentication failed"


class TestAdPlatformFactory:
    def test_register_and_create(self):
        factory = AdPlatformFactory()
        factory.register("google_ads", GoogleAdsManager)
        manager = factory.create("google_ads", credentials={"api_key": "test"})
        assert isinstance(manager, GoogleAdsManager)

    def test_create_unknown_platform_raises(self):
        factory = AdPlatformFactory()
        with pytest.raises(ValueError, match="No ad platform manager registered"):
            factory.create("tiktok_ads", credentials={})

    def test_list_platforms(self):
        factory = AdPlatformFactory()
        factory.register("google_ads", GoogleAdsManager)
        factory.register("facebook_ads", FacebookAdsManager)
        platforms = factory.list_platforms()
        assert "google_ads" in platforms
        assert "facebook_ads" in platforms


class TestGoogleAdsManager:
    @pytest.fixture
    def manager(self):
        return GoogleAdsManager(credentials={"api_key": "test_key"})

    @pytest.mark.asyncio
    async def test_create_ad_returns_mock_result(self, manager):
        result = await manager.create_ad(
            headline="Test Headline",
            description="Test description.",
            final_url="https://example.com",
        )
        assert result.success is True
        assert result.platform == "google_ads"
        assert result.ad_id is not None

    @pytest.mark.asyncio
    async def test_pause_ad(self, manager):
        result = await manager.pause_ad("ad_123")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_resume_ad(self, manager):
        result = await manager.resume_ad("ad_123")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_delete_ad(self, manager):
        result = await manager.delete_ad("ad_123")
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_credentials(self, manager):
        result = await manager.validate_credentials()
        assert result is True


class TestFacebookAdsManager:
    @pytest.fixture
    def manager(self):
        return FacebookAdsManager(credentials={"access_token": "test_token"})

    @pytest.mark.asyncio
    async def test_create_ad_returns_mock_result(self, manager):
        result = await manager.create_ad(
            headline="Test",
            description="Test description.",
            final_url="https://example.com",
        )
        assert result.success is True
        assert result.platform == "facebook_ads"
        assert result.ad_id is not None

    @pytest.mark.asyncio
    async def test_pause_ad(self, manager):
        result = await manager.pause_ad("ad_456")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_delete_ad(self, manager):
        result = await manager.delete_ad("ad_456")
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_credentials(self, manager):
        result = await manager.validate_credentials()
        assert result is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_ads/test_ad_platforms.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Create the base class**

Create `backend/app/services/ad_platforms/__init__.py` (empty file).

Create `backend/app/services/ad_platforms/base.py`:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AdPlatformResult:
    success: bool
    platform: str
    ad_id: str | None = None
    error: str | None = None
    raw_response: dict | None = field(default=None, repr=False)


class AdPlatformManager(ABC):
    """Abstract base class for ad platform managers."""

    platform: str = ""

    def __init__(self, credentials: dict):
        self.credentials = credentials

    @abstractmethod
    async def create_ad(
        self, headline: str, description: str, final_url: str, **kwargs
    ) -> AdPlatformResult:
        ...

    @abstractmethod
    async def pause_ad(self, ad_id: str) -> AdPlatformResult:
        ...

    @abstractmethod
    async def resume_ad(self, ad_id: str) -> AdPlatformResult:
        ...

    @abstractmethod
    async def delete_ad(self, ad_id: str) -> bool:
        ...

    @abstractmethod
    async def validate_credentials(self) -> bool:
        ...
```

- [ ] **Step 4: Create the factory**

Create `backend/app/services/ad_platforms/factory.py`:

```python
from app.services.ad_platforms.base import AdPlatformManager


class AdPlatformFactory:
    """Registry and factory for ad platform managers."""

    def __init__(self):
        self._registry: dict[str, type[AdPlatformManager]] = {}

    def register(self, platform: str, manager_class: type[AdPlatformManager]):
        self._registry[platform] = manager_class

    def create(self, platform: str, credentials: dict) -> AdPlatformManager:
        manager_class = self._registry.get(platform)
        if not manager_class:
            raise ValueError(
                f"No ad platform manager registered for '{platform}'. "
                f"Available: {', '.join(self._registry.keys())}"
            )
        return manager_class(credentials=credentials)

    def list_platforms(self) -> list[str]:
        return list(self._registry.keys())
```

- [ ] **Step 5: Create Google Ads mock manager**

Create `backend/app/services/ad_platforms/google_ads.py`:

```python
import uuid

from app.services.ad_platforms.base import AdPlatformManager, AdPlatformResult


class GoogleAdsManager(AdPlatformManager):
    """Google Ads manager. Currently returns mock results for development."""

    platform = "google_ads"

    async def create_ad(
        self, headline: str, description: str, final_url: str, **kwargs
    ) -> AdPlatformResult:
        # Mock: generate a fake ad ID. Replace with real Google Ads API call.
        ad_id = f"gad_{uuid.uuid4().hex[:12]}"
        return AdPlatformResult(
            success=True,
            platform=self.platform,
            ad_id=ad_id,
            raw_response={"headline": headline, "description": description, "final_url": final_url},
        )

    async def pause_ad(self, ad_id: str) -> AdPlatformResult:
        return AdPlatformResult(success=True, platform=self.platform, ad_id=ad_id)

    async def resume_ad(self, ad_id: str) -> AdPlatformResult:
        return AdPlatformResult(success=True, platform=self.platform, ad_id=ad_id)

    async def delete_ad(self, ad_id: str) -> bool:
        return True

    async def validate_credentials(self) -> bool:
        return True
```

- [ ] **Step 6: Create Facebook Ads mock manager**

Create `backend/app/services/ad_platforms/facebook_ads.py`:

```python
import uuid

from app.services.ad_platforms.base import AdPlatformManager, AdPlatformResult


class FacebookAdsManager(AdPlatformManager):
    """Facebook Ads manager. Currently returns mock results for development."""

    platform = "facebook_ads"

    async def create_ad(
        self, headline: str, description: str, final_url: str, **kwargs
    ) -> AdPlatformResult:
        ad_id = f"fb_{uuid.uuid4().hex[:12]}"
        return AdPlatformResult(
            success=True,
            platform=self.platform,
            ad_id=ad_id,
            raw_response={"headline": headline, "description": description, "final_url": final_url},
        )

    async def pause_ad(self, ad_id: str) -> AdPlatformResult:
        return AdPlatformResult(success=True, platform=self.platform, ad_id=ad_id)

    async def resume_ad(self, ad_id: str) -> AdPlatformResult:
        return AdPlatformResult(success=True, platform=self.platform, ad_id=ad_id)

    async def delete_ad(self, ad_id: str) -> bool:
        return True

    async def validate_credentials(self) -> bool:
        return True
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_ads/test_ad_platforms.py -v`
Expected: All 12 tests PASS

- [ ] **Step 8: Commit**

```bash
git add backend/app/services/ad_platforms/ backend/tests/test_ads/test_ad_platforms.py
git commit -m "feat(ads): add ad platform abstraction with Google/Facebook mock managers"
```

---

### Task 5: Ads Campaign Router (CRUD)

**Files:**
- Create: `backend/app/modules/ads/router.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_ads/test_ad_router.py`

- [ ] **Step 1: Write campaign CRUD router tests**

Create `backend/tests/test_ads/test_ad_router.py`:

```python
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
import json

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.site import Site
from app.models.ad import AdCampaign, Ad


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    user = User(
        email="router@test.com",
        name="Router Tester",
        google_id="google_router_123",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def site(db_session: AsyncSession, user: User) -> Site:
    site = Site(
        user_id=user.id,
        url="https://example.com",
        name="Test Site",
        description="A test site",
        niche="finance",
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site


@pytest.fixture
async def campaign(db_session: AsyncSession, user: User, site: Site) -> AdCampaign:
    campaign = AdCampaign(
        site_id=site.id,
        user_id=user.id,
        name="Test Campaign",
        platform="google_ads",
        objective="traffic",
        daily_budget_cents=5000,
        status="draft",
    )
    db_session.add(campaign)
    await db_session.commit()
    await db_session.refresh(campaign)
    return campaign


@pytest.fixture
async def ad(db_session: AsyncSession, campaign: AdCampaign) -> Ad:
    ad = Ad(
        campaign_id=campaign.id,
        headline="Test Headline",
        description="Test description for the ad.",
        final_url="https://example.com",
        status="draft",
    )
    db_session.add(ad)
    await db_session.commit()
    await db_session.refresh(ad)
    return ad


class TestCampaignCRUD:
    @pytest.mark.asyncio
    async def test_create_campaign(self, db_session: AsyncSession, user: User, site: Site):
        from app.modules.ads.router import _create_campaign_in_db

        campaign = await _create_campaign_in_db(
            db=db_session,
            site_id=str(site.id),
            user_id=user.id,
            name="New Campaign",
            platform="google_ads",
            objective="traffic",
            daily_budget_cents=5000,
            status="draft",
        )
        assert campaign.name == "New Campaign"
        assert campaign.platform == "google_ads"
        assert campaign.daily_budget_cents == 5000

    @pytest.mark.asyncio
    async def test_list_campaigns(self, db_session: AsyncSession, user: User, site: Site):
        for i in range(3):
            db_session.add(AdCampaign(
                site_id=site.id,
                user_id=user.id,
                name=f"Campaign {i}",
                platform="google_ads",
                objective="traffic",
                daily_budget_cents=1000 * (i + 1),
                status="draft",
            ))
        await db_session.commit()

        result = await db_session.execute(
            select(AdCampaign).where(AdCampaign.site_id == site.id)
        )
        campaigns = result.scalars().all()
        assert len(campaigns) == 3

    @pytest.mark.asyncio
    async def test_update_campaign(self, db_session: AsyncSession, campaign: AdCampaign):
        campaign.name = "Updated Campaign"
        campaign.daily_budget_cents = 8000
        await db_session.commit()
        await db_session.refresh(campaign)

        assert campaign.name == "Updated Campaign"
        assert campaign.daily_budget_cents == 8000

    @pytest.mark.asyncio
    async def test_delete_campaign(self, db_session: AsyncSession, campaign: AdCampaign):
        campaign_id = campaign.id
        await db_session.delete(campaign)
        await db_session.commit()

        result = await db_session.execute(
            select(AdCampaign).where(AdCampaign.id == campaign_id)
        )
        assert result.scalar_one_or_none() is None


class TestAdCRUD:
    @pytest.mark.asyncio
    async def test_create_ad(self, db_session: AsyncSession, campaign: AdCampaign):
        from app.modules.ads.router import _create_ad_in_db

        ad = await _create_ad_in_db(
            db=db_session,
            campaign_id=str(campaign.id),
            headline="New Ad",
            description="A new ad description.",
            final_url="https://example.com",
            status="draft",
        )
        assert ad.headline == "New Ad"
        assert ad.campaign_id == campaign.id

    @pytest.mark.asyncio
    async def test_list_ads_by_campaign(self, db_session: AsyncSession, campaign: AdCampaign):
        for i in range(3):
            db_session.add(Ad(
                campaign_id=campaign.id,
                headline=f"Ad {i}",
                description=f"Description {i}",
                final_url="https://example.com",
                status="draft",
            ))
        await db_session.commit()

        result = await db_session.execute(
            select(Ad).where(Ad.campaign_id == campaign.id)
        )
        ads = result.scalars().all()
        assert len(ads) == 3

    @pytest.mark.asyncio
    async def test_update_ad(self, db_session: AsyncSession, ad: Ad):
        ad.headline = "Updated Headline"
        await db_session.commit()
        await db_session.refresh(ad)
        assert ad.headline == "Updated Headline"

    @pytest.mark.asyncio
    async def test_delete_ad(self, db_session: AsyncSession, ad: Ad):
        ad_id = ad.id
        await db_session.delete(ad)
        await db_session.commit()

        result = await db_session.execute(select(Ad).where(Ad.id == ad_id))
        assert result.scalar_one_or_none() is None


class TestAdGeneration:
    @pytest.mark.asyncio
    async def test_generate_ad_copy_integration(self, db_session: AsyncSession, campaign: AdCampaign, site: Site):
        """Test that generated ad variants can be saved to DB."""
        variants = [
            {"headline": "Track Investments", "description": "AI-powered tracking."},
            {"headline": "Smart Finance", "description": "Real-time insights."},
        ]
        ads = []
        for v in variants:
            ad = Ad(
                campaign_id=campaign.id,
                headline=v["headline"],
                description=v["description"],
                final_url="https://example.com",
                status="draft",
            )
            db_session.add(ad)
            ads.append(ad)
        await db_session.commit()

        result = await db_session.execute(
            select(Ad).where(Ad.campaign_id == campaign.id)
        )
        saved = result.scalars().all()
        assert len(saved) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_ads/test_ad_router.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.modules.ads.router'`

- [ ] **Step 3: Implement the ads router**

Create `backend/app/modules/ads/router.py`:

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ad import AdCampaign, Ad
from app.models.site import Site
from app.modules.auth.dependencies import get_current_user
from app.modules.ads.schemas import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
    CampaignResponse,
    CampaignListResponse,
    AdCreateRequest,
    AdUpdateRequest,
    AdResponse,
    AdListResponse,
    AdGenerateRequest,
    AdGenerateResponse,
)
from app.services.ad_copy_generator import AdCopyGenerator
from app.services.llm.factory import create_llm_factory

router = APIRouter(prefix="/api/ads", tags=["ads"])


# ── Campaign endpoints ──────────────────────────────────────────────

@router.post("/campaigns/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    request: CampaignCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    campaign = await _create_campaign_in_db(
        db=db,
        site_id=request.site_id,
        user_id=current_user.id,
        name=request.name,
        platform=request.platform,
        objective=request.objective,
        daily_budget_cents=request.daily_budget_cents,
        status=request.status,
        targeting=request.targeting,
        meta_data=request.meta_data,
    )
    return _campaign_to_response(campaign)


@router.get("/campaigns/", response_model=CampaignListResponse)
async def list_campaigns(
    site_id: str = Query(...),
    platform: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = select(AdCampaign).where(AdCampaign.site_id == uuid.UUID(site_id))

    if platform:
        query = query.where(AdCampaign.platform == platform)
    if status_filter:
        query = query.where(AdCampaign.status == status_filter)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(AdCampaign.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    items = result.scalars().all()

    return CampaignListResponse(
        items=[_campaign_to_response(c) for c in items],
        total=total,
    )


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    campaign = await _get_campaign_or_404(db, campaign_id)
    return _campaign_to_response(campaign)


@router.patch("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    request: CampaignUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    campaign = await _get_campaign_or_404(db, campaign_id)
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    await db.commit()
    await db.refresh(campaign)
    return _campaign_to_response(campaign)


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    campaign = await _get_campaign_or_404(db, campaign_id)
    await db.delete(campaign)
    await db.commit()


# ── Ad endpoints ─────────────────────────────────────────────────────

@router.post("/ads/", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
async def create_ad(
    request: AdCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ad = await _create_ad_in_db(
        db=db,
        campaign_id=request.campaign_id,
        headline=request.headline,
        headline_2=request.headline_2,
        headline_3=request.headline_3,
        description=request.description,
        description_2=request.description_2,
        display_url=request.display_url,
        final_url=request.final_url,
        image_url=request.image_url,
        status=request.status,
        meta_data=request.meta_data,
    )
    return _ad_to_response(ad)


@router.get("/ads/", response_model=AdListResponse)
async def list_ads(
    campaign_id: str = Query(...),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = select(Ad).where(Ad.campaign_id == uuid.UUID(campaign_id))

    if status_filter:
        query = query.where(Ad.status == status_filter)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Ad.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    items = result.scalars().all()

    return AdListResponse(
        items=[_ad_to_response(a) for a in items],
        total=total,
    )


@router.get("/ads/{ad_id}", response_model=AdResponse)
async def get_ad(
    ad_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ad = await _get_ad_or_404(db, ad_id)
    return _ad_to_response(ad)


@router.patch("/ads/{ad_id}", response_model=AdResponse)
async def update_ad(
    ad_id: str,
    request: AdUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ad = await _get_ad_or_404(db, ad_id)
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ad, field, value)
    await db.commit()
    await db.refresh(ad)
    return _ad_to_response(ad)


@router.delete("/ads/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad_endpoint(
    ad_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ad = await _get_ad_or_404(db, ad_id)
    await db.delete(ad)
    await db.commit()


# ── Ad generation endpoint ───────────────────────────────────────────

@router.post("/generate", response_model=AdGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_ads(
    request: AdGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Verify site exists
    site_result = await db.execute(
        select(Site).where(Site.id == uuid.UUID(request.site_id))
    )
    site = site_result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Verify campaign exists
    await _get_campaign_or_404(db, request.campaign_id)

    site_context = {"product_name": site.name, "url": site.url}
    if site.description:
        site_context["description"] = site.description
    if site.niche:
        site_context["niche"] = site.niche

    factory = create_llm_factory()
    llm = factory.get(
        current_user.default_llm_provider,
        api_key=current_user.openai_api_key,
    )
    generator = AdCopyGenerator(llm=llm)

    variants = await generator.generate(
        platform=request.platform,
        topic=request.topic,
        num_variants=request.num_variants,
        site_context=site_context,
        tone=request.tone,
        keywords=request.keywords,
    )

    # Save each variant as a draft ad
    ads = []
    for v in variants:
        ad = Ad(
            campaign_id=uuid.UUID(request.campaign_id),
            headline=v.get("headline", ""),
            headline_2=v.get("headline_2"),
            headline_3=v.get("headline_3"),
            description=v.get("description", ""),
            description_2=v.get("description_2"),
            final_url=site.url,
            status="draft",
        )
        db.add(ad)
        ads.append(ad)

    await db.commit()
    for ad in ads:
        await db.refresh(ad)

    return AdGenerateResponse(ads=[_ad_to_response(a) for a in ads])


# ── Helpers ──────────────────────────────────────────────────────────

async def _create_campaign_in_db(
    db: AsyncSession,
    site_id: str,
    user_id: uuid.UUID,
    name: str,
    platform: str,
    objective: str,
    daily_budget_cents: int,
    status: str,
    targeting: dict | None = None,
    meta_data: dict | None = None,
) -> AdCampaign:
    campaign = AdCampaign(
        site_id=uuid.UUID(site_id),
        user_id=user_id,
        name=name,
        platform=platform,
        objective=objective,
        daily_budget_cents=daily_budget_cents,
        status=status,
        targeting=targeting,
        meta_data=meta_data,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def _create_ad_in_db(
    db: AsyncSession,
    campaign_id: str,
    headline: str,
    description: str,
    final_url: str,
    status: str = "draft",
    headline_2: str | None = None,
    headline_3: str | None = None,
    description_2: str | None = None,
    display_url: str | None = None,
    image_url: str | None = None,
    meta_data: dict | None = None,
) -> Ad:
    ad = Ad(
        campaign_id=uuid.UUID(campaign_id),
        headline=headline,
        headline_2=headline_2,
        headline_3=headline_3,
        description=description,
        description_2=description_2,
        display_url=display_url,
        final_url=final_url,
        image_url=image_url,
        status=status,
        meta_data=meta_data,
    )
    db.add(ad)
    await db.commit()
    await db.refresh(ad)
    return ad


async def _get_campaign_or_404(db: AsyncSession, campaign_id: str) -> AdCampaign:
    result = await db.execute(
        select(AdCampaign).where(AdCampaign.id == uuid.UUID(campaign_id))
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


async def _get_ad_or_404(db: AsyncSession, ad_id: str) -> Ad:
    result = await db.execute(
        select(Ad).where(Ad.id == uuid.UUID(ad_id))
    )
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad


def _campaign_to_response(campaign: AdCampaign) -> CampaignResponse:
    return CampaignResponse(
        id=str(campaign.id),
        site_id=str(campaign.site_id),
        user_id=str(campaign.user_id),
        name=campaign.name,
        platform=campaign.platform,
        objective=campaign.objective,
        daily_budget_cents=campaign.daily_budget_cents,
        status=campaign.status,
        targeting=campaign.targeting,
        meta_data=campaign.meta_data,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )


def _ad_to_response(ad: Ad) -> AdResponse:
    return AdResponse(
        id=str(ad.id),
        campaign_id=str(ad.campaign_id),
        headline=ad.headline,
        headline_2=ad.headline_2,
        headline_3=ad.headline_3,
        description=ad.description,
        description_2=ad.description_2,
        display_url=ad.display_url,
        final_url=ad.final_url,
        image_url=ad.image_url,
        status=ad.status,
        platform_ad_id=ad.platform_ad_id,
        meta_data=ad.meta_data,
        created_at=ad.created_at,
        updated_at=ad.updated_at,
    )
```

- [ ] **Step 4: Register the ads router in main.py**

Add to `backend/app/main.py` after the content router import:

```python
    from app.modules.ads.router import router as ads_router
    app.include_router(ads_router)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest tests/test_ads/test_ad_router.py -v`
Expected: All 9 tests PASS

- [ ] **Step 6: Run full test suite for regression**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest -v`
Expected: All existing + new tests PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/modules/ads/router.py backend/app/main.py backend/tests/test_ads/test_ad_router.py
git commit -m "feat(ads): add campaigns and ads CRUD router with generation endpoint"
```

---

### Task 6: Full Integration Verification

**Files:** None new — this is a verification-only task.

- [ ] **Step 1: Run the full test suite**

Run: `cd /home/arun/market/amplifi/backend && python -m pytest -v --tb=short`
Expected: All tests PASS (116 existing + ~47 new = ~163 total)

- [ ] **Step 2: Verify no import errors by loading the app**

Run: `cd /home/arun/market/amplifi/backend && python -c "from app.main import app; print('App loaded, routes:', [r.path for r in app.routes])"`
Expected: Output includes `/api/ads/campaigns/`, `/api/ads/ads/`, `/api/ads/generate` among others.

- [ ] **Step 3: Commit any remaining changes**

```bash
git status
# If clean, no action needed. If stray files, add and commit.
```
