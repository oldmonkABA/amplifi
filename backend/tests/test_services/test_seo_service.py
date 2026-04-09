import json
from unittest.mock import AsyncMock

import pytest

from app.services.seo_service import SEOService


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    return llm


@pytest.fixture
def seo_service(mock_llm):
    return SEOService(llm=mock_llm)


@pytest.mark.asyncio
async def test_research_keywords(seo_service, mock_llm):
    mock_llm.generate.return_value = json.dumps({
        "keywords": [
            {"term": "ai marketing automation", "estimated_volume": 12000, "difficulty": 45},
            {"term": "automated content generation", "estimated_volume": 8000, "difficulty": 35},
            {"term": "marketing ai tools", "estimated_volume": 6000, "difficulty": 50},
        ]
    })

    result = await seo_service.research_keywords(
        niche="marketing_technology",
        seed_keywords=["ai marketing", "content automation"],
        count=3,
    )

    assert len(result) == 3
    assert result[0]["term"] == "ai marketing automation"
    assert result[0]["estimated_volume"] == 12000
    assert result[0]["difficulty"] == 45


@pytest.mark.asyncio
async def test_research_keywords_with_competitor(seo_service, mock_llm):
    mock_llm.generate.return_value = json.dumps({
        "keywords": [
            {"term": "buffer alternative", "estimated_volume": 3000, "difficulty": 30},
        ]
    })

    result = await seo_service.research_keywords(
        niche="marketing_technology",
        seed_keywords=["social media scheduler"],
        competitors=["Buffer", "Hootsuite"],
        count=1,
    )

    assert len(result) == 1
    # Verify competitor info was included in prompt
    call_args = mock_llm.generate.call_args
    prompt = call_args[1].get("prompt", call_args[0][0] if call_args[0] else "")
    assert "Buffer" in prompt


@pytest.mark.asyncio
async def test_optimize_content(seo_service, mock_llm):
    mock_llm.generate.return_value = json.dumps({
        "optimized_title": "10 Best AI Marketing Automation Tools for 2026",
        "meta_description": "Discover the top AI marketing automation tools that can transform your content strategy in 2026. Compare features, pricing, and more.",
        "suggested_headings": [
            "What is AI Marketing Automation?",
            "Top AI Marketing Tools Compared",
            "How to Choose the Right Tool",
        ],
        "keyword_density_suggestions": {
            "ai marketing automation": "Use 3-5 times in a 2000-word article",
            "marketing tools": "Use 2-3 times",
        },
        "internal_linking_suggestions": [
            "Link to your SEO guide when mentioning optimization",
            "Reference your pricing page in the comparison section",
        ],
    })

    result = await seo_service.optimize_content(
        content="Here is my draft article about marketing tools...",
        target_keywords=["ai marketing automation", "marketing tools"],
        content_type="blog",
    )

    assert "optimized_title" in result
    assert "meta_description" in result
    assert len(result["meta_description"]) <= 320  # Meta descriptions should be reasonable length
    assert "suggested_headings" in result


@pytest.mark.asyncio
async def test_identify_content_gaps(seo_service, mock_llm):
    mock_llm.generate.return_value = json.dumps({
        "content_gaps": [
            {
                "topic": "AI marketing ROI calculator",
                "reason": "High search volume, no existing content covers this",
                "suggested_format": "interactive tool + blog post",
                "estimated_impact": "high",
            },
            {
                "topic": "Marketing automation vs manual comparison",
                "reason": "Common search query with limited quality results",
                "suggested_format": "detailed comparison article",
                "estimated_impact": "medium",
            },
        ]
    })

    result = await seo_service.identify_content_gaps(
        niche="marketing_technology",
        existing_content_titles=["AI Marketing Guide", "Getting Started with Automation"],
        competitor_urls=["https://buffer.com/blog", "https://hootsuite.com/blog"],
    )

    assert len(result) == 2
    assert result[0]["topic"] == "AI marketing ROI calculator"
    assert result[0]["estimated_impact"] == "high"


@pytest.mark.asyncio
async def test_research_keywords_handles_bad_json(seo_service, mock_llm):
    mock_llm.generate.return_value = "Not valid JSON response"

    result = await seo_service.research_keywords(
        niche="marketing",
        seed_keywords=["test"],
    )

    assert result == []


@pytest.mark.asyncio
async def test_optimize_content_handles_bad_json(seo_service, mock_llm):
    mock_llm.generate.return_value = "This is not JSON"

    result = await seo_service.optimize_content(
        content="Some content",
        target_keywords=["test"],
    )

    assert "error" in result or "raw_response" in result
