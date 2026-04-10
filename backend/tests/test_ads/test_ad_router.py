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
