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
