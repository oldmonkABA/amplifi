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
