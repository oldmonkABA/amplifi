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
