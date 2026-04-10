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
