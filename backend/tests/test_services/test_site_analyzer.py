from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.services.site_analyzer import SiteAnalyzer


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.generate.return_value = """{
        "product_name": "Amplifi",
        "description": "AI-powered marketing automation platform",
        "niche": "marketing_technology",
        "key_features": ["content generation", "SEO optimization", "scheduling"],
        "target_audience": "startups and small businesses",
        "competitors": ["Buffer", "Hootsuite", "HubSpot"],
        "tone": "professional",
        "unique_selling_points": ["AI-powered", "multi-platform", "SEO-integrated"]
    }"""
    return llm


@pytest.fixture
def analyzer(mock_llm):
    return SiteAnalyzer(llm=mock_llm)


@pytest.mark.asyncio
async def test_analyze_scraped_content(analyzer):
    html_content = """
    <html>
    <head><title>Amplifi - AI Marketing</title>
    <meta name="description" content="AI-powered marketing automation"></head>
    <body>
    <h1>Amplifi</h1>
    <p>Generate content for 11 platforms with AI.</p>
    <p>SEO optimization built in.</p>
    </body>
    </html>
    """
    result = await analyzer.analyze_html(html_content, "https://amplifi.example.com")

    assert result["product_name"] == "Amplifi"
    assert result["niche"] == "marketing_technology"
    assert "content generation" in result["key_features"]
    assert len(result["competitors"]) > 0


@pytest.mark.asyncio
async def test_analyze_extracts_text_from_html(analyzer, mock_llm):
    html_content = """
    <html><body>
    <h1>My Product</h1>
    <script>var x = 1;</script>
    <style>.hidden{display:none}</style>
    <p>This is the actual content.</p>
    </body></html>
    """
    await analyzer.analyze_html(html_content, "https://example.com")

    # Verify LLM was called with cleaned text (no script/style tags)
    call_args = mock_llm.generate.call_args
    prompt = call_args[1]["prompt"] if "prompt" in call_args[1] else call_args[0][0]
    assert "var x = 1" not in prompt
    assert "display:none" not in prompt
    assert "actual content" in prompt


@pytest.mark.asyncio
async def test_analyze_handles_llm_json_error(mock_llm):
    mock_llm.generate.return_value = "This is not valid JSON at all"
    analyzer = SiteAnalyzer(llm=mock_llm)

    result = await analyzer.analyze_html(
        "<html><body><p>Test</p></body></html>", "https://example.com"
    )
    assert result is not None
    assert "error" in result or "raw_response" in result


@pytest.mark.asyncio
async def test_extract_metadata(analyzer):
    html_content = """
    <html>
    <head>
    <title>Amplifi - Marketing AI</title>
    <meta name="description" content="AI marketing automation platform">
    <meta name="keywords" content="ai, marketing, automation">
    <meta property="og:title" content="Amplifi">
    <meta property="og:description" content="Automate your marketing">
    </head>
    <body><p>Content here</p></body>
    </html>
    """
    metadata = analyzer.extract_metadata(html_content)

    assert metadata["title"] == "Amplifi - Marketing AI"
    assert metadata["meta_description"] == "AI marketing automation platform"
    assert "ai" in metadata["meta_keywords"]
    assert metadata["og_title"] == "Amplifi"
    assert metadata["og_description"] == "Automate your marketing"
