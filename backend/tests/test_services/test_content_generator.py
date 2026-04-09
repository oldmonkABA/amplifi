from unittest.mock import AsyncMock

import pytest

from app.services.content_generator import ContentGenerator, PLATFORM_CONFIGS


def test_platform_configs_exist():
    """All supported platforms have generation configs."""
    expected_platforms = [
        "twitter", "linkedin", "reddit", "blog", "medium",
        "quora", "telegram", "youtube", "hackernews", "producthunt", "email",
    ]
    for platform in expected_platforms:
        assert platform in PLATFORM_CONFIGS, f"Missing config for {platform}"
        config = PLATFORM_CONFIGS[platform]
        assert "max_length" in config
        assert "system_prompt" in config


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    return llm


@pytest.fixture
def generator(mock_llm):
    return ContentGenerator(llm=mock_llm)


@pytest.mark.asyncio
async def test_generate_tweet(generator, mock_llm):
    mock_llm.generate.return_value = "Just launched Amplifi v2! AI-powered content for 11 platforms. Check it out: https://amplifi.dev #marketing #ai"

    result = await generator.generate(
        platform="twitter",
        content_type="tweet",
        topic="Product launch announcement",
        site_context={"product_name": "Amplifi", "niche": "marketing_technology"},
        tone="professional",
        keywords=["ai", "marketing"],
    )

    assert result["title"] is not None
    assert result["body"] is not None
    assert result["platform"] == "twitter"
    assert result["content_type"] == "tweet"

    # Verify LLM was called with appropriate prompt
    call_args = mock_llm.generate.call_args
    prompt = call_args[1].get("prompt", call_args[0][0] if call_args[0] else "")
    assert "twitter" in prompt.lower() or "tweet" in prompt.lower()


@pytest.mark.asyncio
async def test_generate_blog_post(generator, mock_llm):
    mock_llm.generate.return_value = """# 10 AI Marketing Strategies for 2026

AI is transforming how businesses approach marketing. Here are the top strategies...

## 1. Automated Content Generation

Content generation has become more sophisticated...

## 2. SEO Optimization

With AI-powered SEO tools, businesses can...

## Conclusion

The future of marketing is AI-powered. Start implementing these strategies today."""

    result = await generator.generate(
        platform="blog",
        content_type="article",
        topic="AI marketing strategies for 2026",
        site_context={"product_name": "Amplifi", "niche": "marketing_technology"},
        tone="authoritative",
        keywords=["ai marketing", "marketing automation", "seo"],
    )

    assert result["platform"] == "blog"
    assert result["content_type"] == "article"
    assert len(result["body"]) > 100


@pytest.mark.asyncio
async def test_generate_linkedin_post(generator, mock_llm):
    mock_llm.generate.return_value = "Excited to share that we have launched Amplifi v2!\n\nKey highlights:\n- AI content for 11 platforms\n- Built-in SEO\n- Smart scheduling\n\nLink in comments.\n\n#MarketingAutomation #AI"

    result = await generator.generate(
        platform="linkedin",
        content_type="post",
        topic="Product launch",
        site_context={"product_name": "Amplifi", "niche": "marketing_technology"},
    )

    assert result["platform"] == "linkedin"
    assert result["content_type"] == "post"


@pytest.mark.asyncio
async def test_generate_with_additional_context(generator, mock_llm):
    mock_llm.generate.return_value = "Check out Amplifi for your marketing needs!"

    result = await generator.generate(
        platform="twitter",
        content_type="tweet",
        topic="Product recommendation",
        site_context={"product_name": "Amplifi"},
        additional_context="We just hit 1000 users this week",
    )

    call_args = mock_llm.generate.call_args
    prompt = call_args[1].get("prompt", call_args[0][0] if call_args[0] else "")
    assert "1000 users" in prompt


@pytest.mark.asyncio
async def test_generate_reddit_post(generator, mock_llm):
    mock_llm.generate.return_value = "Title: [Show] Amplifi - AI marketing automation that actually works\n\nBody: Hey everyone, I built this tool that generates content for 11 platforms using AI. Would love your feedback.\n\nWhat it does:\n- Generates platform-specific content\n- Built-in SEO optimization\n- Smart scheduling across timezones"

    result = await generator.generate(
        platform="reddit",
        content_type="post",
        topic="Show HN style product launch",
        site_context={"product_name": "Amplifi", "niche": "marketing_technology"},
        tone="conversational",
    )

    assert result["platform"] == "reddit"


@pytest.mark.asyncio
async def test_generate_youtube_script(generator, mock_llm):
    mock_llm.generate.return_value = """TITLE: How Amplifi Uses AI to Automate Your Marketing

DESCRIPTION: In this video, we explore how Amplifi uses AI to generate content across 11 platforms. Learn about automated SEO, smart scheduling, and more.

SCRIPT:
[INTRO]
Hey everyone, welcome back to the channel. Today we are diving into how AI is changing the game for marketing automation.

[MAIN CONTENT]
First, let us talk about content generation...

[OUTRO]
If you found this helpful, hit that subscribe button."""

    result = await generator.generate(
        platform="youtube",
        content_type="script",
        topic="Product demo walkthrough",
        site_context={"product_name": "Amplifi"},
    )

    assert result["platform"] == "youtube"
    assert result["content_type"] == "script"
