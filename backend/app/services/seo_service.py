import json
import re


class SEOService:
    """SEO research and optimization service powered by LLM."""

    def __init__(self, llm):
        self.llm = llm

    def _parse_json_response(self, response: str) -> dict | None:
        """Try to parse a JSON response from the LLM, handling markdown fences."""
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            return None

    async def research_keywords(
        self,
        niche: str,
        seed_keywords: list[str],
        competitors: list[str] | None = None,
        count: int = 10,
    ) -> list[dict]:
        """Research keywords for a niche using LLM.

        Returns a list of dicts with 'term', 'estimated_volume', and 'difficulty' keys.
        """
        prompt_parts = [
            "You are an SEO keyword research expert.",
            "",
            f"Niche: {niche}",
            f"Seed keywords: {', '.join(seed_keywords)}",
        ]

        if competitors:
            prompt_parts.append(f"Competitors: {', '.join(competitors)}")

        prompt_parts.extend([
            "",
            f"Generate {count} keyword suggestions. For each keyword, estimate the "
            "monthly search volume and keyword difficulty (0-100 scale).",
            "",
            "Return ONLY valid JSON in this format:",
            '{"keywords": [{"term": "keyword here", "estimated_volume": 1000, "difficulty": 50}]}',
        ])

        response = await self.llm.generate(prompt="\n".join(prompt_parts))
        parsed = self._parse_json_response(response)

        if parsed and "keywords" in parsed:
            return parsed["keywords"]
        return []

    async def optimize_content(
        self,
        content: str,
        target_keywords: list[str],
        content_type: str = "blog",
    ) -> dict:
        """Analyze content and suggest SEO optimizations.

        Returns a dict with optimized title, meta description, heading suggestions, etc.
        """
        # Truncate very long content
        max_chars = 6000
        content_preview = content[:max_chars] + "..." if len(content) > max_chars else content

        prompt = f"""You are an SEO content optimization expert.

Content type: {content_type}
Target keywords: {', '.join(target_keywords)}

Content to optimize:
{content_preview}

Analyze this content and return ONLY valid JSON with these fields:
- optimized_title: an SEO-optimized title (under 60 characters)
- meta_description: an SEO-optimized meta description (under 160 characters)
- suggested_headings: list of H2/H3 headings to include
- keyword_density_suggestions: dict of keyword to usage recommendation
- internal_linking_suggestions: list of internal linking opportunities

Return ONLY valid JSON, no markdown fences or explanation."""

        response = await self.llm.generate(prompt=prompt)
        parsed = self._parse_json_response(response)

        if parsed:
            return parsed
        return {"raw_response": response, "error": "Failed to parse optimization suggestions"}

    async def identify_content_gaps(
        self,
        niche: str,
        existing_content_titles: list[str],
        competitor_urls: list[str] | None = None,
    ) -> list[dict]:
        """Identify content gaps in the current content strategy.

        Returns a list of content gap dicts with topic, reason, suggested_format, and impact.
        """
        prompt_parts = [
            "You are an SEO content strategist.",
            "",
            f"Niche: {niche}",
            f"Existing content: {', '.join(existing_content_titles)}",
        ]

        if competitor_urls:
            prompt_parts.append(f"Competitor sites: {', '.join(competitor_urls)}")

        prompt_parts.extend([
            "",
            "Identify content gaps — topics that are missing from the existing content "
            "strategy that could drive organic traffic.",
            "",
            "Return ONLY valid JSON in this format:",
            '{"content_gaps": [{"topic": "...", "reason": "...", "suggested_format": "...", "estimated_impact": "high|medium|low"}]}',
        ])

        response = await self.llm.generate(prompt="\n".join(prompt_parts))
        parsed = self._parse_json_response(response)

        if parsed and "content_gaps" in parsed:
            return parsed["content_gaps"]
        return []
