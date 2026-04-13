PLATFORM_CONFIGS = {
    "twitter": {
        "max_length": 280,
        "system_prompt": (
            "You are a social media expert specializing in Twitter/X. "
            "Write concise, engaging tweets that drive engagement. "
            "Use relevant hashtags sparingly (1-3). Stay under 280 characters. "
            "Do NOT use markdown formatting. Plain text only."
        ),
    },
    "linkedin": {
        "max_length": 3000,
        "system_prompt": (
            "You are a LinkedIn content strategist. Write professional, "
            "insightful posts that establish thought leadership. Use line breaks "
            "for readability. Include a call to action. Use relevant hashtags (3-5). "
            "IMPORTANT: Do NOT use markdown formatting (no **, no ##, no bullet points with -). "
            "LinkedIn does not render markdown. Use plain text, line breaks, and emojis for structure."
        ),
    },
    "reddit": {
        "max_length": 10000,
        "system_prompt": (
            "You are a Reddit-savvy content creator. Write authentic, "
            "community-focused posts. Avoid sounding promotional. Be genuine, "
            "share value, and invite discussion. Format with a clear title and body."
        ),
    },
    "blog": {
        "max_length": 50000,
        "system_prompt": (
            "You are an SEO-focused blog writer. Write well-structured articles "
            "with H2/H3 headings, clear paragraphs, and actionable insights. "
            "Naturally incorporate target keywords. Include an introduction, "
            "main sections, and a conclusion with a call to action."
        ),
    },
    "medium": {
        "max_length": 30000,
        "system_prompt": (
            "You are a Medium writer. Write engaging, story-driven articles "
            "that blend personal insight with practical advice. Use a conversational "
            "tone. Include a compelling hook in the first paragraph."
        ),
    },
    "quora": {
        "max_length": 5000,
        "system_prompt": (
            "You are a Quora expert. Write helpful, authoritative answers "
            "that directly address the question. Include relevant experience "
            "or data. Naturally mention the product where appropriate with a backlink."
        ),
    },
    "telegram": {
        "max_length": 4096,
        "system_prompt": (
            "You are a Telegram channel manager. Write concise, informative "
            "updates. Use emoji sparingly for visual breaks. Keep messages "
            "scannable and include links where relevant."
        ),
    },
    "youtube": {
        "max_length": 50000,
        "system_prompt": (
            "You are a YouTube content creator. Write video scripts with clear "
            "sections: TITLE, DESCRIPTION (for SEO), and SCRIPT with [INTRO], "
            "[MAIN CONTENT], and [OUTRO] markers. Write in a conversational, "
            "engaging tone. Include a description optimized for YouTube search."
        ),
    },
    "hackernews": {
        "max_length": 5000,
        "system_prompt": (
            "You are launching a product on Hacker News. Write a concise, "
            "technical launch post. Focus on the technology, what problem it "
            "solves, and the unique approach. Avoid marketing speak. Be honest "
            "about limitations. The HN community values authenticity."
        ),
    },
    "producthunt": {
        "max_length": 3000,
        "system_prompt": (
            "You are launching on Product Hunt. Write an engaging product "
            "description with a catchy tagline, clear value proposition, "
            "key features as bullet points, and a maker comment. Be enthusiastic "
            "but genuine."
        ),
    },
    "email": {
        "max_length": 20000,
        "system_prompt": (
            "You are an email marketing expert. Write compelling email content "
            "with an attention-grabbing subject line, personalized greeting, "
            "clear value proposition, and strong call to action. Keep paragraphs "
            "short for mobile readability."
        ),
    },
}


class ContentGenerator:
    """Generates platform-specific content using LLM."""

    def __init__(self, llm):
        self.llm = llm

    async def generate(
        self,
        platform: str,
        content_type: str,
        topic: str,
        site_context: dict | None = None,
        tone: str = "professional",
        keywords: list[str] | None = None,
        additional_context: str | None = None,
    ) -> dict:
        config = PLATFORM_CONFIGS.get(platform)
        if not config:
            raise ValueError(f"Unsupported platform: {platform}")

        prompt = self._build_prompt(
            platform=platform,
            content_type=content_type,
            topic=topic,
            site_context=site_context or {},
            tone=tone,
            keywords=keywords or [],
            additional_context=additional_context,
            config=config,
        )

        response = await self.llm.generate(prompt=prompt)

        title = self._extract_title(response, topic, platform)
        body = response.strip()

        return {
            "platform": platform,
            "content_type": content_type,
            "title": title,
            "body": body,
        }

    def _build_prompt(
        self,
        platform: str,
        content_type: str,
        topic: str,
        site_context: dict,
        tone: str,
        keywords: list[str],
        additional_context: str | None,
        config: dict,
    ) -> str:
        parts = [config["system_prompt"], ""]

        if site_context:
            context_str = ", ".join(f"{k}: {v}" for k, v in site_context.items())
            parts.append(f"Product context: {context_str}")

        parts.append(f"Platform: {platform}")
        parts.append(f"Content type: {content_type}")
        parts.append(f"Topic: {topic}")
        parts.append(f"Tone: {tone}")

        if keywords:
            parts.append(f"Target keywords: {', '.join(keywords)}")

        if additional_context:
            parts.append(f"Additional context: {additional_context}")

        parts.append(f"Maximum length: {config['max_length']} characters")
        parts.append("")
        # Platforms that don't support markdown
        no_markdown = {"twitter", "linkedin", "telegram", "reddit", "quora", "producthunt"}
        if platform in no_markdown:
            parts.append(
                "FORMATTING: Use plain text only. No markdown (no **, ##, -, ```). "
                "Use line breaks and emojis for structure instead."
            )

        parts.append(
            f"Write a {content_type} for {platform} about the topic above. "
            f"Match the specified tone and naturally incorporate any target keywords."
        )

        return "\n".join(parts)

    def _extract_title(self, response: str, fallback_topic: str, platform: str) -> str:
        lines = response.strip().split("\n")
        first_line = lines[0].strip()

        # Check for markdown heading
        if first_line.startswith("#"):
            return first_line.lstrip("#").strip()

        # Check for TITLE: prefix (youtube format)
        if first_line.upper().startswith("TITLE:"):
            return first_line[6:].strip()

        # Check for Title: prefix (reddit format)
        if first_line.startswith("Title:"):
            return first_line[6:].strip()

        # For short-form content, use topic as title
        if platform in ("twitter", "telegram"):
            return fallback_topic

        # Use first line if it looks like a title (short enough)
        if len(first_line) < 120:
            return first_line

        return fallback_topic
