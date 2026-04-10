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
